metadata_aliases = {
    'all': ['description', 'nullable', 'required'],
    'number': [
        'minimum',
        'maximum',
        'exclusive_minimum',
        'exclusive_maximum',
        'multiple_of',
    ],
    'string': ['min_length', 'max_length', 'format', 'pattern'],
    'array': ['one_of', 'min_items', 'max_items', 'unique_items'],
    'object': ['min_properties', 'max_properties'],
}
