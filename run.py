from flask import Flask, request, redirect, url_for, render_template
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache

RENDER_INDEX_BOOTSTRAP="index_bootstrap.html"
RENDER_INDEX="index_new.html"
RENDER_TABLE_DATA="table_data_new.html"
RENDER_TABLE_DATA_IMG="table_data_img.html"
STATIC_URL_PATH = "static/"


# environment variable
PORT = os.getenv('PORT', '5000')



app = Flask(__name__) 
Bootstrap(app)

logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue="DEBUG",
            flaskapp=app)

logger = logs.logger 




def get_debug_all(request):
    str_debug = '* url: {}\n* method:{}\n'.format(request.url, request.method)
    str_debug += '* Args:\n'
    for entry in request.args:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry, request.args[entry])
    str_debug += '* Headers:\n'
    for entry in request.headers:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry[0], entry[1])
    return str_debug

@app.route('/', methods=['GET'])
def root():
    try :
        if (postgres.__checkHerokuLogsTable()):
            postgres.__saveLogEntry(request)

        logger.debug(get_debug_all(request))
        rediscache.__display_RedisContent()
        """
        key = {'url' : request.url}
        tmp_dict = None
        data_dict = None
        tmp_dict = __getCache(key)
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")
            data_dict  = __getTables()
            __setCache(key, ujson.dumps(data_dict), 300)
        else:
            logger.info("Data found in redis, using it directly")
            data_dict = ujson.loads(tmp_dict)
        """
        data_dict  = postgres.__getTables()
        
        return render_template(RENDER_INDEX,
                            entries=data_dict['data'])
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200


@app.route('/error', methods=['GET'])
def error():
    if (postgres.__checkHerokuLogsTable()):
        postgres.__saveLogEntry(request)


    logger.debug(get_debug_all(request))
    logger.error("Generating Error")
    error_code = 500
    if ('error_code' in request.args):
        error_code = int(request.args['error_code'])
    return "Error !!!!!!",error_code


@app.route('/getObjects', methods=['GET'])
def getObjects():
    try: 
        if (postgres.__checkHerokuLogsTable()):
            postgres.__saveLogEntry(request)
        # output type
        output='html'
        if 'output' in request.args:
            output = request.args['output'].lower()
        
        # logs all attributes received
        logger.debug(get_debug_all(request))
        # gets object name
        object_name=''
        if ('name' in request.args):
            object_name = request.args['name']
        else:
            return "Error, must specify a object name with ?name=xxx", 404
            
        key = {'url' : request.url, 'output' : output}
        tmp_dict = None
        data_dict = None
        tmp_dict = rediscache.__getCache(key)
        data = ""
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")
            data_dict  = postgres.__getObjects(object_name) 

            if (output == 'html'):
                logger.info("Treating request as a web request, output to Web page")
                if ('image__c' in data_dict['columns']):
                            data = render_template(RENDER_TABLE_DATA_IMG,
                            columns=data_dict['columns'],
                            object_name=object_name,
                            entries = data_dict['data'])
                else:
                    data = render_template(RENDER_TABLE_DATA,
                                columns=data_dict['columns'],
                                object_name=object_name,
                                entries = data_dict['data'])

            else:
                logger.info("Treating request as an API request, output to Json only")
                data = ujson.dumps(data_dict)

            if (postgres.HEROKU_LOGS_TABLE not in request.url): # we don't want to cache these logs
                rediscache.__setCache(key, data.encode('utf-8'), 300)

        else:
            logger.info("Data found in redis, using it directly")
            #logger.info(tmp_dict)
            if (output == 'html'):
            #data_dict = ujson.loads(tmp_dict)
                data = tmp_dict.decode('utf-8')
            else:
                #data = ujson.loads(tmp_dict)
                data = tmp_dict

        logger.info("returning data")
        return data, 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200



if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=int(PORT))




