import tensorflow as tf
from pathlib import Path

def get_models(root_dir):
    file_list = []
    for file_path in Path(root_dir).rglob("*/saved_model.pb"):
        if file_path.is_file():
            file_list.append((str(file_path), str(file_path.parent)))
    return file_list


for file, path in get_models("./"):
    print(file)
    model = tf.saved_model.load(path)
    concrete_func = model.signatures[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY]
    tf.io.write_graph(concrete_func.graph, path, 'model.pb', as_text=False)