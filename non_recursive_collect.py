# Danbooru Image Collector
import shutil
import sys
import os
import requests
import winsound as ws
from time import sleep
from datetime import datetime

global keywords_d
global keywords_string
global keywords_key
global keywords_value
global exdir
global copydir
global gAuth


class DownloadNum:
    downloadNum = 0

    def __init__(self):
        self.downloadNum = 0

    def init_dw_num(self):
        self.downloadNum = 0

    def increase_dw_num(self):
        self.downloadNum += 1

    def get_dw_num(cls):
        return str(cls.downloadNum)


dn = DownloadNum()


def beepsound(times, freq, dur):
    frequency = freq  # range : 37 ~ 32767
    duration = dur  # ms
    for time in range(times):
        ws.Beep(frequency, duration)  # winsound.Beep(frequency, duration)
    return ''

now = datetime.now()


def setDataStr(dataStr: list, page: int):
    dataStr.append('{ "post": { "tags": "')
    dataStr.append(keywords_value)
    dataStr.append(' rating:safe" }, "page": ')
    dataStr.append(str(page))
    dataStr.append(' }')
    dataStr = ''.join(dataStr)

    return dataStr


def getSizeSTR(downloadPath: str):
    filesize = os.path.getsize(downloadPath)

    if filesize / 1024 >= 10240:
        sizeSTR = fr'({str(round(float(filesize) / (1024 ** 2), 1))}MB)'
    elif filesize / 1024 >= 1024:
        sizeSTR = fr'({str(round(float(filesize) / (1024 ** 2), 2))}MB)'
    else:
        sizeSTR = fr'({str(round(float(filesize) / 1024))}KB)'

    return sizeSTR


def printProgress(iteration, total, prefix='', suffix='', decimals=1, barLength=100):
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '#' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r' + fr'{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()


def Main():
    global gAuth
    # 경로 설정
    filedir = fr'{exdir}'
    fileDotArtist_txt = open(fr'{filedir}\(0)FileNArtist.txt', 'wt', encoding='utf-8')
    f_list = os.listdir(filedir)

    url = 'https://danbooru.donmai.us/posts.json'
    sHeaders = {
        'Content-Type': 'application/json',
    }
    page = 1
    sData = []
    sData = setDataStr(sData, page)

    try:
        res = requests.get(url, headers=sHeaders, data=sData, auth=gAuth)
        res.raise_for_status()  # 페이지 연결상태 확인
        pics = res.json()
    except requests.ConnectionError:
        print(beepsound(2, 1500, 50))
        while True:
            print('서버 응답 대기중1..')
            sleep(0.3)
            res = requests.get(url, headers=sHeaders, data=sData, auth=gAuth)
            pics = res.json()
            if res.status_code == 200:
                break
    dn.init_dw_num()
    totalNum = 0
    newPicsList = []

    # Main loop Start
    exit_flag = 1
    while exit_flag != 0:
        for j in range(len(pics)):
            totalNum += 1
            picURL = pics[j]['file_url']
            artistName = pics[j]['tag_string_artist']
            charactersName = pics[j]['tag_string_character']
            tag_string_general = pics[j]['tag_string_general']

            filename = os.path.basename(picURL)
            downloadPath = os.path.join(filedir, filename)
            if filename in f_list:
                print(fr'{page} - {j + 1} [////////////////////]', end='')
                if j % 2 == 0:
                    print('\t\t ', end='')
                else:
                    print('\n', end='')
                fileDotArtist_txt.write(fr'{filename} | {artistName} | {charactersName} | {tag_string_general}\n\n')
                fileDotArtist_txt.close()
                fileDotArtist_txt = open(fr'{filedir}\(0)FileNArtist.txt', 'at', encoding='utf-8')
                continue
            else:
                printProgress(0, 100, fr'{page} - {j + 1}', fr'Downloading', 1, 20)
                try:
                    res = requests.get(picURL, auth=gAuth)
                    fullSize = int(res.headers['content-length'])
                    res.raise_for_status()
                except requests.ConnectionError:
                    print(beepsound(2, 1500, 50))
                    while True:
                        print('서버 응답 대기중2..')
                        sleep(0.3)
                        res = requests.get(picURL, auth=gAuth)
                        if res.status_code == 200:
                            break

                # Download Start
                start_s = datetime.now()
                imageFile = open(downloadPath, 'wb')

                for chunk in res.iter_content(5000):
                    imageFile.write(chunk)
                    downloadedSize = os.path.getsize(downloadPath)
                    tick_s = datetime.now()
                    printProgress(downloadedSize, fullSize, fr'{page} - {j + 1}', fr'Downloading{"." * (tick_s - start_s).seconds}', 1, 20)
                imageFile.close()

                sizeSTR = getSizeSTR(downloadPath)
                printProgress(100, 100, fr'{page} - {j + 1}', fr'{filename}{sizeSTR} is Downloaded.', 1, 20)
                # Download Done

                # Copy to upload
                # copyPath = os.path.join(copydir, filename)
                # shutil.copy(downloadPath, copyPath)

                fileDotArtist_txt.write(filename + ' | ' + artistName + ' | ' + tag_string_general + '\n\n')
                fileDotArtist_txt.close()
                fileDotArtist_txt = open(fr'{filedir}\(0)FileNArtist.txt', 'at', encoding='utf-8')
                newPicsList.append(filename)

                if j % 2 == 0:
                    print('\t\t ', end='')
                else:
                    var = None
                dn.increase_dw_num()
                print('\n', end='')

        print((fr'{str(page)} page done.' + '\n'), beepsound(1, 440, 100))

        # Next page
        page += 1

        # Use for daily Collecting
        # if page > 5:
        #     exit_flag = 0
        #     fileDotArtist_txt.close()
        #     break

        sData = []
        sData = setDataStr(sData, page)
        try:
            res = requests.get(url, headers=sHeaders, data=sData, auth=gAuth)
            res.raise_for_status()
            pics = res.json()
        except requests.ConnectionError:
            print(beepsound(2, 1500, 50))
            while True:
                print('서버 응답 대기중3..')
                sleep(0.3)
                res = requests.get(url, headers=sHeaders, data=sData, auth=gAuth)
                pics = res.json()
                if res.status_code == 200:
                    break
        if len(pics) == 0:
            exit_flag = 0
            fileDotArtist_txt.close()
            break
    # End of while
    print(beepsound(2, 880, 100))

    print('\n', end='')
    print('Done..!')
    print(fr'총 {page - 1}페이지의 ', end='')
    print(fr'{totalNum}장 중 {dn.get_dw_num()}장이 새로 저장되었습니다.' + '\n\n')


# 검색 키워드
keywords_d = {'helltaker': 'helltaker',
              'default'  : ''}

# 폴더 이름({exdir}\{keywords_string})
keywords_string = {'helltaker': '헬테이커',
                   'default'  : ''}

gAuth = ('ID', 'API Key')
HOMEFULLPATH = os.getenv('HOMEDRIVE') + os.getenv('HOMEPATH')

def setPath(aKey):
    global keywords_key
    global keywords_value
    global exdir
    global copydir

    if aKey not in keywords_d:
        print('There\'s not key matched ' + aKey)
        sys.exit(-1)

    keywords_key   = aKey
    keywords_value = keywords_d[aKey]
    exdir    = fr'{HOMEFULLPATH}\Pictures\{keywords_string[aKey]}'
    copydir  = fr'{HOMEFULLPATH}\Pictures\{keywords_string[aKey]}\(0)업로드용'


if __name__ == '__main__':
    if len(sys.argv) > 1:
        setPath(sys.argv[1])
    else:
        setPath('helltaker')

    os.makedirs(fr'{exdir}', exist_ok=True)
    os.makedirs(fr'{copydir}', exist_ok=True)

    if os.path.exists(fr'{exdir}\(0)dailyLog.txt'):
        dailyLog_txt = open(fr'{exdir}\(0)dailyLog.txt', 'at', encoding='utf-8')
    else:
        dailyLog_txt = open(fr'{exdir}\(0)dailyLog.txt', 'wt', encoding='utf-8')
    dailyLog_txt.write(fr'{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}:{now.second} start.' + '\n')
    dailyLog_txt.close()

    if os.path.exists(copydir):
        for file in os.scandir(copydir):
            os.remove(file.path)
    else:
        os.makedirs(fr'{copydir}', exist_ok=True)

    Main()

    endtime = datetime.now()
    dailyLog_txt = open(fr'{exdir}\(0)dailyLog.txt', 'at', encoding='utf-8')
    dailyLog_txt.write('\n' + fr'{endtime.year}-{endtime.month}-{endtime.day} {endtime.hour}:{endtime.minute}:{endtime.second} end.' + '\n\n')
    dailyLog_txt.close()

    print()
    f = open(fr'{exdir}\(0)dailyLog.txt', 'r', encoding='utf-8')
    lines = f.readlines()
    resultLine = lines[-3:]
    for line in resultLine:
        print(line, end='')
    f.close()
    print()

    print(beepsound(5, 1760, 300))
