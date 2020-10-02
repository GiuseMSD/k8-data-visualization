import requests
import json
import pandas as pd 
from pandas import json_normalize
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from bokeh.io import show, output_file
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool, WheelZoomTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.palettes import Spectral4
import warnings
warnings.filterwarnings('ignore')

class Issues:

    def __init__(self, repos):
        self.repos          = repos
        git_token           = '86734524155dfbb7f7130dd405fb74a55f100d36'
        self.git_headers    = {'Authorization': f'token {git_token}'}
        zen_token           = 'c3bd1d296da6c51afa652dcd51cbd33f712ebec8bde25cd9b05d2b4279b8003a1226cb2e2da152fd'
        self.zen_headers    = {'X-Authentication-token': zen_token}
        self.zen_ws_id      = '5f43aa60e9220900139f4fb3'
        self.configure_pandas()
        self.df         = self.init_df()

    def init_df(self):
        try:
            dfs         = []
            for repo in self.repos:
                url                     = f'https://api.github.com/repos/{repo[0]}/issues'
                res                     = requests.get(url, headers=self.git_headers, params={'state': 'all'}).json()
                zen_url                 = f'https://api.zenhub.com/p2/workspaces/{self.zen_ws_id}/repositories/{repo[1]}/board'
                zen_pipeline            = requests.get(zen_url, headers=self.zen_headers).json()
                zen_pipeline = zen_pipeline['pipelines'] if 'pipelines' in zen_pipeline.keys() else []
                for issue in res:
                    number = issue['number']
                    pipe_name = ''
                    flag = False
                    for panel in zen_pipeline:
                        panel_issues = panel['issues']
                        for item in panel_issues:
                            if item['issue_number'] == number:
                                pipe_name  = panel['name']
                                flag        = True
                                break
                        if flag == True:
                            break
                    issue['pipeline'] = pipe_name
                data                    = json_normalize(res, max_level=1)
                temp_df                 = pd.DataFrame(data)
                temp_df['repo']         = repo[0]
                dfs.append(temp_df)
            df                          = pd.concat(dfs, ignore_index=True)
            return df
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def get_df(self):
        return self.df

    def configure_pandas(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.expand_frame_repr', False)

    def normalize_data(self):
        df                      = self.df
        df                      = df[['created_at','user.login', 'user.url','author_association', 'title','body', 'state', 'repo', 'pipeline', 'assignee.login']]
        df['created_at']        = pd.to_datetime(df['created_at']).dt.date
        self.df                 = df

    def show_pie(self, column):
        plt.figure                             (figsize = (8,8))
        self.df[column].value_counts().plot(kind    = 'pie', autopct = '%.2f', fontsize = 20)
        plt.show()

    def show_bar_chart_by_repo(self):
        plt.figure                             (figsize = (15,10))
        self.df["repo"].value_counts().plot.bar(title   = "Bar Chart Showing Number of Issues By Repo")
        plt.ylabel('Number of Issues')
        plt.xlabel('Repo')
        plt.show()

    def show_bar_chart_by_date(self):
        plt.figure                             (figsize = (40,10))
        sns.countplot(self.df['created_at'],    label   = "Number of Issues")
        plt.show()        

    def show_grid_chart(self, column):
        df        = self.df
        keys      = [pair for pair, x in df.groupby([column])]
        plt.figure(figsize=(15,10))
        plt.plot  (keys, df.groupby([column]).count())
        plt.xticks(keys)
        plt.grid  ()
        plt.show  ()

    def show_bar_chart_by_user(self):
        df        = self.df
        user      = df.groupby('user.login')
        response  = user.count()['created_at']
        keys      = [pair for pair, df in user]
        plt.figure(figsize = (10,10))
        plt.bar   (keys, response)
        plt.xticks(keys, rotation='vertical', size=8)
        plt.ylabel('Number of Issues')
        plt.xlabel('Users')
        plt.show()       
         
    def show_en_graph(self):
        df                  = self.df
        df                  = df.rename({'user.login':'dusers'}, axis=1)
        issues              = list(df.title.unique())
        users               = list(df.dusers.unique())
        plt.figure(figsize=(12, 12))
        g                   = nx.from_pandas_edgelist(df, source='dusers', target='title', edge_attr='dusers') 
        layout              = nx.spring_layout(g,iterations=50)

        nx.draw_networkx_edges(g, layout, edge_color='#AAAAAA')
        users               = [node for node in g.nodes() if node in df.dusers.unique()]
        size                = [g.degree(node) * 80 for node in g.nodes() if node in df.dusers.unique()]

        nx.draw_networkx_nodes(g, layout, nodelist=users, node_size=size, node_color='lightblue')
        issues              = [node for node in g.nodes() if node in df.title.unique()]

        nx.draw_networkx_nodes(g, layout, nodelist=issues, node_size=100, node_color='#AAAAAA')
        high_degree_issues  = [node for node in g.nodes() if node in df.title.unique() and g.degree(node) > 1]

        nx.draw_networkx_nodes(g, layout, nodelist=high_degree_issues, node_size=100, node_color='#fc8d62')
        user_dict           = dict(zip(users, users))
        
        nx.draw_networkx_labels(g, layout, labels=user_dict)
        plt.axis    ('off')
        plt.title   ("Network Graph of Users and the Issues generated")
        plt.show()
    
    # Exporting Interactive Graph
        TOOLTIPS = [
    ("name", "@dusers"),
]
        plot                                            = Plot(x_range=Range1d(-1.1,1.1), y_range=Range1d(-1.1,1.1))
        plot.title.text                                 = "Network Graph of Users and the Issues generated"
        plot.add_tools(HoverTool(tooltips=TOOLTIPS), TapTool(), BoxSelectTool(), WheelZoomTool())
        graph_renderer                                  = from_networkx(g, nx.spring_layout, scale=1, center=(0,0))
        graph_renderer.node_renderer.glyph              = Circle(size=15, fill_color=Spectral4[0])
        graph_renderer.node_renderer.selection_glyph    = Circle(size=15, fill_color=Spectral4[2])
        graph_renderer.node_renderer.hover_glyph        = Circle(size=15, fill_color=Spectral4[1])
        graph_renderer.edge_renderer.glyph              = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=5)
        graph_renderer.edge_renderer.selection_glyph    = MultiLine(line_color=Spectral4[2], line_width=5)
        graph_renderer.edge_renderer.hover_glyph        = MultiLine(line_color=Spectral4[1], line_width=5)
        graph_renderer.selection_policy                 = NodesAndLinkedEdges()
        graph_renderer.inspection_policy                = EdgesAndLinkedNodes()
        # plot.renderers.append(graph_renderer)
        output_file("interactive_graph.html")
        show(plot)

    def show_tabular_report_by_repo(self):
        df          = self.df
        user        = df.groupby(['repo', 'pipeline'])
        pipe_df      = user['title'].count().unstack(-1, 0)
        return pipe_df

    def show_tabular_report_by_user(self):
        df          = self.df
        user        = df.groupby(['assignee.login', 'pipeline'])
        pipe_df      = user['title'].count().unstack(-1, 0)
        return pipe_df
