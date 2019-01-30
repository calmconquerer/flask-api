from flask import Flask, request, render_template
import dropbox
import config
import os

dbx = dropbox.Dropbox(config.exports['token'])


chunk_size = config.exports['chunkSize'] * 1024 * 1024
max_chunk = config.exports['maxChunk'] * 1024 * 1024
upload_dir = '/Users/Sam/MyApps/Wasi/api/files'

app = Flask(__name__)
app.config['upload_dir'] = upload_dir


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def uploader():
    files = request.files.getlist('file')
    for file in files:
        try:
            filename = file.filename
            destination_path = os.path.join(config.exports['targetFolder'], filename)
            file.seek(0, 2)
            fileSize = file.tell()
            file.seek(0)
            print(fileSize)
            if fileSize <= max_chunk:
                print('hello')
                dbx.files_upload(file.read(), destination_path)
                print('done')
            else:
                upload_session_start_result = dbx.files_upload_session_start(file.stream.read(chunk_size))
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=file.stream.read.tell())
                commit = dropbox.files.CommitInfo(path=config.exports['targetFolder'])

                while file.stream.read.tell() < fileSize:
                    if (fileSize - file.stream.read.tell()) <= chunk_size:
                        print(dbx.files_upload_session_finish(file.read(chunk_size), cursor, commit))
                    else:
                        dbx.files_upload_session_append_v2(file.stream.read(chunk_size), cursor)
                        cursor.offset = file.stream.tell()
        except Exception as err:
            print("Failed to upload {}\n{}".format(file, err))
    print("Finished upload.")
    return render_template('complete.html')


if __name__ == '__main__':
    app.run(debug=True)