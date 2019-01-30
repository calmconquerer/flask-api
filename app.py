from flask import Flask, request, render_template
import dropbox
import config
import os


dbx = dropbox.Dropbox(config.exports['token'])


chunk_size = config.exports['chunkSize'] * 1024 * 1024
max_chunk = config.exports['maxChunk'] * 1024 * 1024

# Flask(__name__) Starts the flask server
app = Flask(__name__)

# Made a simple form from where I send the files and test if my api is working


@app.route('/')
def index():
    return render_template('upload.html')


'''
   - When the POST request is made, it checks the files in the request.
   
   - Firstly it reads the contents of the files from start to finish and checks the size of the incoming file and stores
     it into the fileSize variable

   - After that it sets the file pointer back to the start so that the file can be read again
   
   - Then the app checks if the size of the file is less than the max chunk size, which is set in the configuration file,
     and starts to upload it directly if the size is less than the max chunk size.
     
   - Keep in mind that the DropBox api uploads the file in one shot to DropBox if it's <= 150 MB but I have set the max 
     chunk size to 2 MB due to my internet connection.

   - If the file size exceeds the max chunk size, then an upload session is created which basically reads chunks of 1 MB
     and sends the chunks to DropBox.
    
   - Finally it checks the file to see if it has reached the final chunk and finishes the session otherwise it keeps on 
     sending chunks to DropBox until the file comes to an end
'''


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
            if fileSize <= max_chunk:
                dbx.files_upload(file.read(), destination_path)
            else:
                print('hello')
                upload_session_start_result = dbx.files_upload_session_start(file.read(chunk_size))
                cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                                           offset=file.tell())
                commit = dropbox.files.CommitInfo(path=destination_path)

                while file.tell() < fileSize:
                    if (fileSize - file.tell()) <= chunk_size:
                        print(dbx.files_upload_session_finish(file.read(chunk_size), cursor, commit))
                    else:
                        dbx.files_upload_session_append_v2(file.read(chunk_size), cursor)
                        cursor.offset = file.tell()
        except Exception as err:
            print("Failed to upload {}\n{}".format(file, err))
        finally:
            file.close()
    print("Finished upload.")
    return render_template('complete.html')


if __name__ == '__main__':
    app.run(debug=True)