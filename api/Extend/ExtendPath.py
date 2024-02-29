from pathlib import Path

def find_target_dir(current_file: str, target_folder: str) -> Path:
    """
    現在のファイルから親ディレクトリを遡り、指定したフォルダ名を探します。

    Parameters:
    current_file (str): 現在のファイルのパス
    target_folder (str): 検索対象のフォルダ名

    Returns:
    Path: 対象フォルダへのパス
    """
    current_path = Path(current_file).resolve()
    while current_path.name != target_folder and current_path != current_path.parent:
        current_path = current_path.parent

    if current_path.name == target_folder:
        return current_path
    else:
        raise FileNotFoundError(f"'{target_folder}' folder not found in the path hierarchy of the current file.")