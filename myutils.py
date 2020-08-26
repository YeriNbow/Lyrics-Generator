def progress_bar(count, length):
    bar = count * '#' + (length - count) * '-'
    print(f'\r{bar} {count} {length}', end='')
