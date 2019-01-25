from flask import Flask, request, render_template
import dropbox
import config
import os

dbx = dropbox.Dropbox(config.exports['token'])


chunk_size = config.exports['chunkSize'] * 1024 * 1024
max_chunk = config.exports['maxChunk']
upload_dir = '/Users/Sam/MyApps/Wasi/api/files'

app = Flask(__name__)
app.config['upload_dir'] = upload_dir


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def uploader():
    file = request.stream.read()
    try:
        # filename = os.path.basename(file)
        # file_path = os.path.abspath(file)
        # destination_path = os.path.join(config.exports['targetFolder'], filename)
        print('Uploading as')
        # if fileSize <= max_chunk:
        #     if file == '.DS_Store':  # A mac user will understand
        #         pass
        #     else:
        dbx.files_upload(file, config.exports['targetFolder'])
        # else:
        #     upload_session_start_result = dbx.files_upload_session_start(file.read(chunk_size))
        #     cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
        #                                                offset=file.tell())
        #     commit = dropbox.files.CommitInfo(path=config.exports['targetFolder'])
        #
        #     while file.tell() < fileSize:
        #         if (fileSize - file.tell()) <= chunk_size:
        #             print(dbx.files_upload_session_finish(file.read(chunk_size), cursor, commit))
        #         else:
        #             dbx.files_upload_session_append_v2(file.read(chunk_size), cursor)
        #             cursor.offset = file.tell()
    except Exception as err:
        print("Failed to upload {}\n{}".format(file, err))
    print("Finished upload.")
    return render_template('complete.html')


if __name__ == '__main__':
    app.run(debug=True)