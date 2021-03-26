def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    flattened_list = list_of_lists[:1] + flatten(list_of_lists[1:])
    flattened_list2 = []
    for i in flattened_list:
        if i not in flattened_list2:
            flattened_list2.append(i)
    return flattened_list2


