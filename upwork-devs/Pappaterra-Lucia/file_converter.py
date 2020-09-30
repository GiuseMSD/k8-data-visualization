import pandas as pd
import yaml
import csv
import os


def xlsx_to_csv(xlsxfile, sheetname):

    data = pd.read_excel(xlsxfile, sheetname, index_col=None)
    # drop unnamed columns
    
    if sheetname == 'Upwork People List' or sheetname == 'Offboarded People':
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        
    elif sheetname == 'Projects Team Structure':
        columns_names = []
        
        for elem in data.iloc[2].tolist():
            columns_names.append(elem.replace('\n', ' '))
            
        data.columns = columns_names
        
        data = data.iloc[3:]
        
        data['Project Name'] = data['Project Name'].apply(lambda s: s.replace('#', '') if isinstance(s, str) else s)
        
        ############# Save Resource and Responsability separately ##############
        data2 = data.copy()
        data2.drop(data2.columns.difference(['Project Name','Resource Name', 'Responsibility for the project']), 1, inplace=True)
        
        # drop empty rows
        data2.replace('', float("NaN"), inplace=True)
        data2.dropna(how='all', inplace=True) 
        
        data2['Project Name'] = data2['Project Name'].ffill()
        data2['Project Name'] = data2['Project Name'].apply(lambda s: s.rstrip('\n'))
                 
        # dropping null value columns to avoid errors 
        data2.dropna(inplace = True)
        
        # replace '–' by '-'
        data2['Resource Name'] = data2['Resource Name'].apply(lambda s: s.replace('–', '-'))
        data2['Responsibility for the project'] = data2['Responsibility for the project'].apply(lambda s: s.replace('–', '-'))
        
        # drop responsability from name column
        data2['Resource Name'] = data2['Resource Name'].apply(lambda s: s.split('-', 1)[0])
        
        # delete spaces and line breaks
        data2['Resource Name'] = data2['Resource Name'].apply(lambda s: s.rstrip('\n').strip() if isinstance(s, str) else s)    
        #data2['Responsability for the project'] = data2['Responsability for the project'].apply(lambda s: s.rstrip('\n').strip() if isinstance(s, str) else s)
        
        # save to csv file
        data2.to_csv('csv_files/Resource and responsability.csv', index=False, encoding='utf-8')
        ########################################################################
        
        data['Delivery Manager'] = data['Delivery Manager'].apply(lambda s: s.rstrip('\n').strip().replace('\n', ', ') if isinstance(s, str) else s)            
        
        data = data.loc[:, ~data.columns.str.contains('Resource Name')]
        data = data.loc[:, ~data.columns.str.contains('Responsibility for the project')]
        
        # drop empty rows
        data.replace('', float("NaN"), inplace=True)
        data.dropna(how='all', inplace=True) 
        
        for col in data.columns:
            data[col] = data[col].apply(lambda s: s.replace('\n', '') if isinstance(s, str) else s)
    
    elif sheetname == 'Skills Matrix':
        h1 = data.iloc[5]
        h1 = h1.tolist()
        h1 = h1[:2]

        h2 = data.iloc[6]
        h2 = h2.tolist()
        h2 = h2[2:]

        data.columns = h1 + h2    
        data = data.iloc[7:]
              
    data.to_csv(os.path.join('csv_files', sheetname+'.csv'), index=False, encoding='utf-8')


def csv_to_yaml(filename):

    csvfile = open(os.path.join('csv_files', filename+'.csv'), 'r')
    datareader = csv.reader(csvfile, delimiter=",", quotechar='"')
    
    result = list()
    type_index = -1
    child_fields_index = -1

    for row_index, row in enumerate(datareader):
        if row_index == 0:
            data_headings = list()
            for heading_index, heading in enumerate(row):
                fixed_heading = heading.lower().replace(" ", "_").replace("-", "")
                data_headings.append(fixed_heading)
                if fixed_heading == "type":
                    type_index = heading_index
                elif fixed_heading == "childfields":
                    child_fields_index = heading_index
        else:
            content = dict()
            is_array = False
            for cell_index, cell in enumerate(row):
                if cell_index == child_fields_index and is_array:
                    content[data_headings[cell_index]] = [{
                    "source" : "fra:" + value.capitalize(),
                    "destination" : value,
                    "type" : "string",
                    "childfields" : "null"
                    } for value in cell.split(",")]
                else:
                    content[data_headings[cell_index]] = cell
                    is_array = (cell_index == type_index) and (cell == "array")
            result.append(content)

    with open(os.path.join('yaml_files',filename+'.yml'), 'w') as f:
        doc = yaml.dump(result, f) 
        