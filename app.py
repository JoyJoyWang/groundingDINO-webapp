
from flask import Flask, request, send_file, jsonify, render_template
from model_inference import run_inference
import os
from PIL import Image
import io
import uuid

# app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='frontend')
app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
UPLOAD_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)

TEXT_PROMPT = "fine crack, crazing, repaired crack, sealed crack, crack with coating, surface-patched crack, hairline. no stone. no ballast. no rail. no wire. no cable. no tube. no shadow. no dark stripe. no graffiti. no stain. no structural shadow."

@app.route("/")
def index():
    # 使用模板渲染 index.html，确保 frontend 目录下有 index.html
    return render_template("index.html")

# @app.route("/upload", methods=["POST"])
# def upload():
#     try:
#         files = request.files.getlist("images")
#         results = []
#         for file in files:
#             # 校验文件类型
#             if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
#                 continue
#             uid = str(uuid.uuid4())[:8]
#             img_path = os.path.join(UPLOAD_DIR, f"{uid}.jpg")
#             file.save(img_path)

#             annotated_img = run_inference(img_path, TEXT_PROMPT)
#             # 校验 annotated_img 格式
#             if hasattr(annotated_img, 'dtype') and hasattr(annotated_img, 'shape'):
#                 output_path = os.path.join(UPLOAD_DIR, f"{uid}_output.jpg")
#                 Image.fromarray(annotated_img).save(output_path)
#                 results.append(f"{uid}_output.jpg")
#             else:
#                 continue
#         return jsonify({"results": results})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload():
    try:
        files = request.files.getlist("images")
        results = []
        for file in files:
            if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            uid = str(uuid.uuid4())[:8]
            img_path = os.path.join(UPLOAD_DIR, f"{uid}.jpg")
            file.save(img_path)

            annotated_img = run_inference(img_path, TEXT_PROMPT)
            print(f"annotated_img type: {type(annotated_img)}")  # Debug

            if hasattr(annotated_img, 'dtype') and hasattr(annotated_img, 'shape'):
                if annotated_img.dtype != np.uint8:
                    annotated_img = np.clip(annotated_img, 0, 255).astype(np.uint8)
                output_path = os.path.join(UPLOAD_DIR, f"{uid}_output.jpg")
                Image.fromarray(annotated_img).save(output_path)
                results.append(f"{uid}_output.jpg")

            else:
                print("annotated_img is invalid")
                continue



        print("results:", results)
        return jsonify({"results": results})

    except Exception as e:
        print("Exception:", e)
        import traceback
        traceback.print_exc()  # 更详细
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
