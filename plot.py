
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
        names = ["Free:\n{0}".format(nb_str(free)),
                 "in Drive:\n{0}".format(nb_str(drive)),
                 "Other:\n{0}".format(nb_str(other))]

        print("\nLimit: {lim}\n".format(lim=gb_str(lim)))

        info = "\nLimit: {lim}\n\n".format(lim=gb_str(lim))
        for name in names:
            print("{0}\n".format(name))
            info += "{0}\n\n".format(name) + '\n'

        my_circle=plt.Circle( (0,0), 0.6, color='white')
        data = [x for x in main_info if x > 0.0]
        labels = [names[i] for i in range(3) if main_info[i] > 0.0]
        patches, texts = plt.pie(data, labels=labels, wedgeprops = { 'linewidth' : 10, 'edgecolor' : 'white' })
        sign = 3
        for patch, txt in zip(patches, texts):
            # the angle at which the text is located
            ang = (patch.theta2 + patch.theta1) / 2.
            # new coordinates of the text, 0.7 is the distance from the center
            x = patch.r * 1 * np.cos(ang*np.pi/180)
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
        plt.savefig('./static/plots/main_info_{0}.png'.format(self.user_id))
        return info

    def top_folders(self, data, n=10):
        plt.figure(figsize=(12,12))
        folders = data[data['type'] == "folder"]
        files = data[data['type'] != "folder"]
        info = ""
        top_files = files.sort_values(by='size', ascending=False).iloc[1:n + 1]
        if (len(folders) <= 1):
            cur_msg = "\nThere are no folders on your disk.\n\nMost heavy files:\n"
            print(cur_msg)
            info += cur_msg + '\n'
            for file in top_files.index:
                cur_msg = "{0} : {1}".format(get_file_path(data, file), nb_str(data.loc[file, 'size']))
                print(cur_msg)
                info += cur_msg + '\n'
            print()

            y_pos = list(range(5))
            heights = top_files.iloc[:5]['size'].values
            bars = top_files.iloc[:5]['name'].values
            # Make the plot
            plt.bar(y_pos, list(map(lambda x: mb(x), heights)))
            plt.xticks(y_pos, bars, fontsize=15, ha='right', rotation=30)
            plt.ylabel('MB' )
            plt.tight_layout()
            plt.savefig('./static/plots/top_folders_{}.png'.format(self.user_id))

            return info
        top_folders = folders.sort_values(by='sum_size', ascending=False).iloc[1:n + 1]

        children = {}
        cur_msg = 'Most heavy folders:'
        print(cur_msg)
        for folder in top_folders.index:
            cur_msg = "{0}:\n {1}".format(get_file_path(data, folder), nb_str(data.loc[folder, 'sum_size']))
            print(cur_msg)
            print()
            info += cur_msg + '\n'
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
        plt.text(150, 380, 'Height - how heavy are files inside.', ha='left', wrap=True, fontsize = 20)
        plt.text(150, 360, 'Width - number of files in folder.', ha='left', wrap=True, fontsize = 20)
        plt.text(150, 320, 'Area - folder size.', ha='left', wrap=True, fontsize = 20)
        plt.text(210, 430, 'The heaviest folders.', ha='left', wrap=True, fontsize = 35)

        plt.tight_layout()
        plt.savefig('./static/plots/top_folders_{}.jpeg'.format(self.user_id))
        return info

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

        #top = sgr.sort_values(by='size', ascending=False).loc[sgr['size'] > 0].iloc[:5]

        info = "Types occupation:\n\n"
        cur_msg = info
        print(cur_msg)
        for typ in gr.values:
            cur_msg = "{0}: {1}".format(typ[1], nb_str(typ[0]))
            print(cur_msg)
            info += cur_msg + '\n'


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

        plt.tight_layout()
        plt.savefig('./static/plots/disk_types_{}.png'.format(self.user_id))
        return info



    def relevant_folders(self, data):
        plt.figure(figsize=(25, 12))

        big_size = data[data['sum_size'] > data['sum_size'].mean()]
        relevant = big_size.sort_values(by='viewedByMeTime')[['name','sum_size','viewedByMeTime']].iloc[:10]
        info = ""
        try:
            height = relevant['viewedByMeTime'].apply(lambda x: get_timeval(x))
        except TypeError:
            cur_msg = 'There is no information about last file visits.'
            print(cur_msg)
            return cur_msg

        cur_msg = 'Most relevant folders to move/delete:\n'
        print(cur_msg)
        info += cur_msg + '\n'
        for id, folder in zip(relevant.index, relevant.values):
            cur_msg = "{0}\nSize: {1}".format(get_file_path(data, id), nb_str(folder[1]))
            print(cur_msg)
            info += cur_msg + '\n'
            cur_msg = "Last visit: {0}\n\n".format(folder[2][:folder[2].find('T')])
            print(cur_msg)
            info += cur_msg

        # Choose the names of the bars
        bars = relevant['name'].values
        y_pos = np.arange(len(bars))
        z = relevant['sum_size'].values

        colors = [plt.get_cmap('summer')(mb(z[i])/mb(z.mean())) for i in range(len(y_pos))]
        plt.bar(y_pos, height, color=colors)

        # Create names on the x-axis
        plt.xticks(y_pos, bars, fontsize=25, rotation=30)
        plt.yticks(fontsize=20)
        plt.ylabel('Days after last visit', fontsize = 25)

        plt.text(6, 550, "Relevant folders.", wrap=True, ha='right', fontsize=50)
        plt.text(8, 480, "Yellow corresponds to the greater size, green - to the less.", wrap=True, ha='right', fontsize=35)

        plt.tight_layout()
        plt.savefig('./static/plots/relevant_{0}.png'.format(self.user_id))
        return info
