class Dog:
    def __init__(self, name):
        """
        :param str name: The name of this dog.
        """
        self._name = name

    @property
    def name(self):
        """
        :returns: The name of this dog.
        :rtype: str
        """
        return self._name

    def bark(self, language='en'):
        """
        Make some noise!

        :param str language: The language to bark in.
        :returns: The bark
        :rtype: str
        """
        if language == 'ru':
            return 'гав!'
        elif language == 'en':
            return 'woof!'
        else:
            raise ValueError('I do not yet know how to bark in %r!' % language)


def main():
    import sys
    from pyannotate_runtime import collect_types
    collect_types.init_types_collection()
    with collect_types.collect():
        dog = Dog('sharik')
        dog.name
        dog.bark('ru')
    collect_types.dump_stats('type_info.json')

if __name__ == '__main__':
    main()
