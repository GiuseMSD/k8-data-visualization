import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from graphviz import Digraph


# Colors
color_set = [plt.cm.tab20(0), plt.cm.tab20(2), plt.cm.tab20(4), plt.cm.tab20(6), 
    plt.cm.tab20(8), plt.cm.tab20(10), plt.cm.tab20(12), plt.cm.tab20(14), 
    plt.cm.tab20(16), plt.cm.tab20(18), plt.cm.tab20(1), plt.cm.tab20(3), 
    plt.cm.tab20(5), plt.cm.tab20(7), plt.cm.tab20(9), plt.cm.tab20(11), 
    plt.cm.tab20(13), plt.cm.tab20(15), plt.cm.tab20(17), plt.cm.tab20(19), 
    plt.cm.tab20b(0), plt.cm.tab20b(2), plt.cm.tab20b(4), plt.cm.tab20b(6), 
    plt.cm.tab20b(8), plt.cm.tab20b(10), plt.cm.tab20b(12), plt.cm.tab20b(14), 
    plt.cm.tab20b(16), plt.cm.tab20b(18), plt.cm.tab20b(1), plt.cm.tab20b(3), 
    plt.cm.tab20b(5), plt.cm.tab20b(7), plt.cm.tab20b(9), plt.cm.tab20b(11), 
    plt.cm.tab20b(13), plt.cm.tab20b(15), plt.cm.tab20b(17), plt.cm.tab20b(19),
    plt.cm.Pastel1(0), plt.cm.Pastel1(1), plt.cm.Pastel1(2), 
    plt.cm.Pastel1(3),plt.cm.Pastel1(4), plt.cm.Pastel1(5),
    plt.cm.Pastel1(6), plt.cm.Pastel1(7), plt.cm.Pastel1(8),
    plt.cm.Set3(0), plt.cm.Set3(1), plt.cm.Set3(2), plt.cm.Set3(3), 
    plt.cm.Set3(4), plt.cm.Set3(5), plt.cm.Set3(6), plt.cm.Set3(7), 
    plt.cm.Set3(8), plt.cm.Set3(9), plt.cm.Set3(10), plt.cm.Set3(11),
    plt.cm.Accent(7), plt.cm.Accent(6), plt.cm.Accent(5), plt.cm.Accent(4),
    plt.cm.Accent(3), plt.cm.Accent(2), plt.cm.Accent(1), plt.cm.Accent(0),
    plt.cm.Dark2(7), plt.cm.Dark2(6), plt.cm.Dark2(5), plt.cm.Dark2(4),
    plt.cm.Dark2(3), plt.cm.Dark2(2), plt.cm.Dark2(1), plt.cm.Dark2(0),
    plt.cm.tab20c(0), plt.cm.tab20c(2), plt.cm.tab20c(4), plt.cm.tab20c(6), 
    plt.cm.tab20c(8), plt.cm.tab20c(10), plt.cm.tab20c(12), plt.cm.tab20c(14), 
    plt.cm.tab20c(16), plt.cm.tab20c(18), plt.cm.tab20c(1), plt.cm.tab20c(3), 
    plt.cm.tab20c(5), plt.cm.tab20c(7), plt.cm.tab20c(9), plt.cm.tab20c(11), 
    plt.cm.tab20c(13), plt.cm.tab20c(15), plt.cm.tab20c(17), plt.cm.tab20c(19)]


def graph(df, df2):
    df['delivery_manager'].replace('', float("NaN"), inplace=True)
    df['delivery_manager'].fillna('No Delivery Managers yet', inplace=True)

    g = Digraph('OrgChart', filename='org_chart.gv')
   
    for p in df['project_name']:
        g.node(p, color='red')
    
        pm = df[df['project_name'] == p]['delivery_manager'].values[0]       
        if pm=='':
            pm = []
        else:
            pm = pm.split(', ')   
         
        rnr = list(df2[df2['project_name'] == p]['resource_name'])
        
        if len(rnr)>0:
            rnr = "\n".join(rnr)
            g.node(rnr, color='green', shape='rectangle')
    
            for elem in pm:
                g.node(elem, color='blue')
                g.edge(p, elem)
                if rnr is not None:
                    g.edge(elem, rnr)
    
    # save graph to pdf                
    g.render('outputs/teams_graph.gv', view=True)   
    return g
    

def bar_plot(df, df2, colors=color_set):

    proj = list(df['project_name'])
    
    rnr = []
    for pr in proj:
        rnr.append(list(df2[df2['project_name']==pr]['resource_name']))
        
    rnr_counts=[]  
    for elem in rnr:
        rnr_counts.append(len(elem))

    fig = plt.figure(figsize=(18,7))
    ax = fig.add_axes([0,0,1,1])
    langs = proj
    
    colors = tuple(colors[:len(proj)])
    
    ax.bar(langs, rnr_counts, color=colors)
       
    # Make some labels
    labels = [str(elem) for elem in rnr_counts]
    rects = ax.patches

    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height, label,
                ha='center', va='bottom')    
    
    plt.title('Amount of resources per project', fontsize=20)
    plt.xticks(rotation=90)
    plt.savefig('outputs/bar_plot.png' , format='png', bbox_inches = 'tight')  
    plt.show()


def pie_chart(df, df2, colors=color_set):
    df['delivery_manager'].replace('', float("NaN"), inplace=True)
    df['delivery_manager'].fillna('No Delivery Managers yet', inplace=True)  

    proj = list(df['project_name'])
    
    rnr = []
    for p in proj:
        rnr.append(list(df2[df2['project_name']==p]['resource_name']))  
    
    pms = convert_to_lists(df['delivery_manager'])
    
    rnr_size = []
    pms_size = []
    group_names = []    
    
    for elem, elem2, elem3 in zip(rnr, pms, proj):
        n = len(elem) 
        if n>0:
            rnr_size.append(n)           
            m = len(elem2) 
            pms_size.append(m)
            group_names.append(elem3)       
            
    group_size = rnr_size

    subgroup_size = []
    for i, j in zip(rnr_size, pms_size):
        if j == 1:
            subgroup_size.append(i)
        else:
            for x in range(j):
                subgroup_size.append(i/j)
 
    fig, ax = plt.subplots(figsize=(12,7))
    ax.set_title("GlassWall Projects \nResources proportion", fontsize=20)

    ax.axis('equal')
    
    colors = colors[:len(proj)]
    
    colors1=[]
    pms2 = []     
    for cr, i in zip(colors, range(len(rnr))):
        rs = rnr[i]           
        if len(rs)>0:
            colors1.append(cr)
            pms2.append(pms[i])
           
    # First Ring (Inside)
    mypie, _ = ax.pie(group_size, radius=1-0.3, colors=colors1) 
    plt.setp(mypie, width=0.4, edgecolor='white')
   
    
    colors2=[]
    for cr, pr, j in zip(colors1, group_names, range(len(pms2))):
        pm = pms2[j]
        if len(pm)>0:
            colors2 = colors2 + [cr] * len(pm)
        else:
            colors2 = colors2 + [cr]    
    
    # Second Ring (Outside)
    mypie2, _ = ax.pie(subgroup_size, radius=1, colors=colors2)                        
    plt.setp(mypie2, width=0.4, edgecolor='white')

    ax.legend(mypie, group_names,
              title="Projects",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")
     
    total_res = sum(rnr_size)
                                 
    resources = []
    for elem in rnr_size:
        resources.append(str(elem) + ' resources ({d}%)'.format(d=round(elem/total_res*100)))
    
    for i, p in enumerate(mypie):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(resources[i], xy=(x, y), xytext=(1.2*np.sign(x), 1.1*y), 
            horizontalalignment=horizontalalignment, **kw)
 
    plt.margins(0,0)  
    
    plt.savefig('outputs/pie_chart.png' , format='png', bbox_inches = 'tight')  

    # show it
    plt.show() 
    
    
def convert_to_lists(df_col):
    ll=[]
    for elem in df_col:
        if elem=='':
            ll.append([]) 
        else:
            ll.append(elem.split(', '))
    return list(ll)  
    