
import matplotlib.pyplot as plt
from matplotlib import cm
from datetime import date
import pandas as pd
import numpy as np
from files_tools import gb_str, mb_str, get_file_path

gig = 1024 * 1024 * 1024

def gb(bytes):
    return bytes/gig

def mb(bytes):
    return bytes/1024/1024

def nb_str(bytes):
    return gb_str(bytes) if bytes > gig else mb_str(bytes)

def get_timeval(datetime, now = pd.to_datetime(date.today())):
    return (now - pd.to_datetime(datetime)).days


class Analyzer():
    def __init__(self, user_id):
        self.user_id = user_id


    def main_info(self, lim, usg, drive):
        plt.figure(figsize=(12,12))

        plt.text(0, 1.4, "Disk Analytics", ha='center', wrap=True, fontsize=70)

        free = lim - usg
        other = usg - drive
        main_info = [free, drive, other]
        names = ["Free\n{0}".format(nb_str(free)),
                 "in Drive\n{0}".format(nb_str(drive)),
                 "Other\n{0}".format(nb_str(other))]

        for name in names:
            print("{0}\n".format(name))

        my_circle=plt.Circle( (0,0), 0.6, color='white')
        data = [x for x in main_info if x > 0.0]
        labels = [names[i] for i in range(3) if main_info[i] > 0.0]
        patches, texts = plt.pie(data, labels=labels, wedgeprops = { 'linewidth' : 10, 'edgecolor' : 'white' })
        sign = 3
        for patch, txt in zip(patches, texts):
            # the angle at which the text is located
            ang = (patch.theta2 + patch.theta1) / 2.
            # new coordinates of the text, 0.7 is the distance from the center
            x = patch.r * 0.7 * np.cos(ang*np.pi/180)
            y = patch.r * 0.7 * np.sin(ang*np.pi/180) * sign
            # if patch is narrow enough, move text to new coordinates
            if (patch.theta2 - patch.theta1) < 10.:
                txt.set_position((x, y))
                sign = -sign

        [txt.set_fontsize(20) for txt in texts]
        p=plt.gcf()
        p.gca().add_artist(my_circle)

        if usg >= 3 * lim / 4:
            advice_1 = "Your disk is almost full."
        elif usg >= lim / 2:
            advice_1 = "Your disk has enough space."
        else:
            advice_1 = "The disk is almost free."

        plt.text(0, -1.5, advice_1, ha='center', wrap=True, fontsize=40)
        plt.tight_layout()
        plt.savefig('main_info_{0}.png'.format(self.user_id))


    def top_folders(self, data, n=10):
        plt.figure(figsize=(12,12))
        folders = data[data['type'] == "folder"]
        files = data[data['type'] != "folder"]

        top_files = files.sort_values(by='size', ascending=False).iloc[1:2*n]
        if (len(folders) <= 1):
            print("\nThere is no folders on your disk.\n")
            print('Most heavy files:')
            for file in top_files.index:
                print("{0} : {1}".format(get_file_path(data, file), nb_str(data.loc[file, 'size'])))
            print()

            y_pos = list(range(5))
            heights = top_files.iloc[:5]['size'].values
            bars = top_files.iloc[:5]['name'].values
            # Make the plot
            plt.bar(y_pos, list(map(lambda x: mb(x), heights)))
            plt.xticks(y_pos, bars, fontsize=15, ha='right', rotation=30)
            plt.ylabel('MB' )
            plt.tight_layout()
            plt.savefig('top_folders_{}.jpeg'.format(self.user_id))

            return 0
        top_folders = folders.sort_values(by='sum_size', ascending=False).iloc[1:n + 1]

        children = {}
        print('Most heavy folders:')
        for folder in top_folders.index:
            print("{0} : {1}".format(get_file_path(data, folder), nb_str(data.loc[folder, 'sum_size'])))
            children[folder] = data[data['parent'] == folder]
        print()


        heights = [mb(top_folders.loc[folder, 'sum_size']) / len(children[folder]) for folder in top_folders.index]
        bars = top_folders['name']

        width = [len(children[folder]) for folder in top_folders.index]
        y_pos = [1]
        for i in range(1, len(width)):
            y_pos.append(y_pos[i - 1] + width[i - 1] / 2 + width[i] / 2 + 30)

        # Make the plot
        plt.bar(y_pos, heights, width=width)
        plt.xticks(y_pos, bars, fontsize=15, rotation=30, ha='right')
        plt.text(150, 380, 'The higher the  bar - the more heavy files it contains.', ha='left', wrap=True, fontsize = 20)
        plt.text(150, 360, 'The broader - the more files it contains.', ha='left', wrap=True, fontsize = 20)
        plt.text(150, 320, 'Firstfull you should look at the highest ones - you can', ha='left', wrap=True, fontsize = 20)
        plt.text(180, 300, 'free a lot of space moving only few file from the Drive.', ha='left', wrap=True, fontsize = 20)
        plt.text(210, 430, 'Most heavy folders.', ha='left', wrap=True, fontsize = 35)

        plt.tight_layout()
        plt.savefig('top_folders_{}.jpeg'.format(self.user_id))

    def calc_type_size(self, typ, data, is_sub=False):
        if is_sub:
            key = data['mimeType'].apply(lambda x: (x.find(typ) != -1) if x else (typ=='other'))
            return data[key]['size'].sum()
        else:
            key = data['type'].apply(lambda x: (x.find(typ) != -1) if x else (typ=='other'))
            return data[key]['size'].sum()

    def disk_types(self, data):
        keywords = {
                'folder' : ['folder'],
                'video' : ['webm', 'video', 'quicktime'],
                'image' : ['jpeg', 'gif', 'bmp'],
                'doc' : ['text', 'plain', 'document', 'djvu', 'pdf', 'msword']}
        data['mimeType'] = data['type'].apply(lambda x: 'other' if not x else x)
        data['type'] = data['type'].apply(lambda x: 'other' if not x else x)

        group_names=data['type'].unique()[1:]

        gr = pd.DataFrame({'size' : [self.calc_type_size(t, data) for t in group_names], 'types' : group_names}).sort_values(by='size', ascending=False)

        subgroup_names=[]
        for l in keywords.values():
            subgroup_names += l
        subgroup_names = subgroup_names[1:]
        sgr = pd.DataFrame({'size' : [self.calc_type_size(t, data, True) for t in subgroup_names], 'types' : subgroup_names})

        top = sgr.sort_values(by='size', ascending=False).loc[sgr['size'] > 0].iloc[:5]

        print("Types occupation:")
        for typ in gr.values:
            print("{0}: {1}".format(typ[1], nb_str(typ[0])))

        if len(top) > 0:
            print("\nMost space-consuming formats:")
            for typ in top.values:
                print("{0}: {1}".format(typ[1], nb_str(typ[0])))


        group_names = list(map(lambda x: "{0}\n{1}".format(x[1], nb_str(x[0])), gr.values))
        # Create colors
        a, b, c, d=[plt.cm.Set1, plt.cm.Blues, plt.cm.Greens, plt.cm.Reds]


        fig, ax = plt.subplots(figsize=(12, 12))
        ax.axis('equal')
        mypie, texts = ax.pie(gr['size'].values, radius=0.8, labels=group_names, colors=[a(0.6), b(0.6), c(0.6), d(0.6)] )
        [txt.set_fontsize(20) for txt in texts]
        sign = 3
        for patch, txt in zip(mypie, texts):
            # the angle at which the text is located
            ang = (patch.theta2 + patch.theta1) / 2.
            # new coordinates of the text, 0.7 is the distance from the center
            x = patch.r * 0.7 * np.cos(ang*np.pi/180)
            y = patch.r * 0.7 * np.sin(ang*np.pi/180) * sign
            # if patch is narrow enough, move text to new coordinates
            if (patch.theta2 - patch.theta1) < 10.:
                txt.set_position((x, y))
                sign = -sign

        plt.setp( mypie, width=0.3, edgecolor='white')
        plt.text(0, 1.1, 'Types and how much do they take.', ha='center', wrap=True, fontsize=25)

        plt.tight_layout()
        plt.savefig('disk_types_{}.png'.format(self.user_id))




    def relevant_folders(self, data):
        plt.figure(figsize=(25, 12))

        big_size = data[data['sum_size'] > data['sum_size'].mean()]
        relevant = big_size.sort_values(by='viewedByMeTime')[['name','sum_size','viewedByMeTime']].iloc[:10]

        try:
            height = relevant['viewedByMeTime'].apply(lambda x: get_timeval(x))
        except TypeError:
            print('There is no information about last file visits.')
            return -1

        print('Most relevant to examine folders:\n')
        for id, folder in zip(relevant.index, relevant.values):
            print("{0}\nSize: {1}".format(get_file_path(data, id), nb_str(folder[1])))
            print("Last visit: {0}\n".format(folder[2][:folder[2].find('T')]))

        # Choose the names of the bars
        bars = relevant['name'].values
        y_pos = np.arange(len(bars))
        z = relevant['sum_size'].values

        colors = [plt.get_cmap('summer')(mb(z[i])/mb(z.mean())) for i in range(len(y_pos))]
        plt.bar(y_pos, height, color=colors)

        # Create names on the x-axis
        plt.xticks(y_pos, bars, fontsize=25, rotation=30)
        plt.yticks(fontsize=20)
        plt.ylabel('Days after last visit')
        plt.xlabel('Folder name')

        plt.text(6, 550, "Relevant folders.", wrap=True, ha='right', fontsize=50)
        plt.text(8, 480, "Yellow corresponds to the greater size, green - to the less.", wrap=True, ha='right', fontsize=35)

        plt.tight_layout()
        plt.savefig('relevant_{0}.png'.format(self.user_id))
