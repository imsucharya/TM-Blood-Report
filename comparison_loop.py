        table = defaultdict(dict)
        for label in all_labels:        # label is Label object
            label_name = label.name
            category = label.category.name
            doc1 = result1_labels.get(label, None)
            doc2 = result2_labels.get(label, None)
            
            if doc1 is not None:
                doc1_value = doc1.get('value', 0)
            else:
                doc1_value = None

            if doc2 is not None:
                doc2_value = doc2.get('value', 0)
            else:
                doc2_value = None
    
            # finding remark value doc2_value - doc1_value
            # remark is Increase or decrease if seconds report values increases or decreases
            # if only single report contains that value then, it is empty

            lower_range = label.lower_range
            upper_range = label.upper_range

            table[label_name]['value'] = doc2_value
            table[label_name]['category'] = category

            if is_single_document:
                try: 
                    if doc2_value < lower_range:
                        table[label_name]['remark'] = 'Low'
                        table[label_name]['remark_color'] = remark_color['Yellow']
                        print('this is single lower remark color', table[label_name]['remark_color'])
                    elif lower_range<= doc2_value <= upper_range:
                        table[label_name]['remark'] = 'Normal'
                        table[label_name]['remark_color'] = remark_color['Green']
                        print('this is single normal remark color', table[label_name]['remark_color'])
                    else:
                        table[label_name]['remark'] = 'High'
                        table[label_name]['remark_color'] = remark_color['Red']
                        print('this is single high remark color', table[label_name]['remark_color'])
                except Exception as e:
                    table[label_name]['remark'] = '-'
                    print('lower_range, upper_range error', e)

            # if label exist for both docs
            elif (doc1 is not None) and (doc2 is not None):
                doc2_value = doc2.get('value', 0)
                doc1_value = doc1.get('value', 0)
                value_change = doc2_value - doc1_value
                try:
                    # previos value was low
                    if doc1_value < label.lower_range: 
                        if value_change<0:                                              # value has gone lower (a)
                            table[label_name]['remark'] = 'Need work'
                            table[label_name]['remark_color'] = remark_color['Pale Yellow']
                        elif value_change==0:                                           # value is same (b)
                            table[label_name]['remark'] = 'Need work'
                            table[label_name]['remark_color'] = remark_color['Yellow']
                        elif value_change>0 and doc2_value < lower_range:               # val is low but not normal (e)
                            table[label_name]['remark'] = 'Improved, Need work'
                            table[label_name]['remark_color'] = remark_color['Pale Green']
                        elif lower_range <= doc2_value <= upper_range:                  # val is normal (c)
                            table[label_name]['remark'] = 'Improved'
                            table[label_name]['remark_color'] = remark_color['Green']
                        elif upper_range < doc2_value:                                  # val has becomne higher (d)
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Red']
                    
                    # if value was normal
                    elif lower_range<=doc1_value<=upper_range:
                        print('value is normal')
                        if value_change<0: # val has gone low
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Yellow']
                        elif lower_range<=doc2_value<=upper_range:
                            table[label_name]['remark'] = ''
                            table[label_name]['remark_color'] = remark_color['White']
                        elif upper_range<doc2_value:
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Red']

                    # if value was high
                    elif upper_range<doc1_value:
                        if value_change>0: # val has gone higher
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Maroon']
                        elif value_change<0 and upper_range<doc2_value: # if val is lower than before still high
                            table[label_name]['remark'] = 'Improved, Need Work'
                            table[label_name]['remark_color'] = remark_color['Pale Green']
                        elif lower_range<=doc2_value<=upper_range:
                            table[label_name]['remark'] = 'Improved'
                            table[label_name]['remark_color'] = remark_color['Green']
                        elif doc2_value < lower_range:
                            table[label_name]['remark'] = 'Need Work'
                            table[label_name]['remark_color'] = remark_color['Yellow']
                except Exception as e:
                    table[label_name]['remark'] = '-'
                    print('No lower upper range error',  label_name, e)
            
            else: # when label exist for only one doc
                table[label_name]['remark'] = '------'
                table[label_name]['remark_color'] = ''
        # table data type from defaultdict to dict
        table = dict(table)
        # print('this is the_table')
        # print(table)
        return table, is_single_document
