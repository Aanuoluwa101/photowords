

def lambda_handler(event, context):
    # get the request body and headers
    headers = event['headers']
    # decode the multipart/form-data request
    postdata = base64.b64decode(event['body'])

    request = {} # Save request here
    
    for part in decoder.MultipartDecoder(postdata, headers['content-type']).parts:

        decoded_header = part.headers[b'Content-Disposition'].decode('utf-8')
        key = get_key(decoded_header)
        request[key] = part.content

    print(request) # This is the request




def get_key(form_data):
    # 'form-data; name="birth_date"', 'content': b'2012-123'
    key = form_data.split(";")[1].split("=")[1].replace('"', '')

    print(key)

    return key