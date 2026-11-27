import os
import shutil

PNG_MAGIC = b'\x89PNG\r\n\x1a\n'

def main():
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(repo_dir, 'entry.png')

    if not os.path.exists(source_path):
        raise SystemExit('entry.png is missing from the repository')

    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR') or 'out'
    os.makedirs(output_dir, exist_ok=True)

    destination_path = os.path.join(output_dir, 'entry.png')
    shutil.copyfile(source_path, destination_path)

    with open(destination_path, 'rb') as f:
        magic = f.read(8)
    if magic != PNG_MAGIC:
        raise SystemExit('destination file is not a valid PNG')

    size = os.path.getsize(destination_path)
    print(destination_path)
    print(size)

if __name__ == '__main__':
    main()