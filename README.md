# ImgCollectorBooru
약간의 설정만으로 기존 하나하나 수동으로 이미지를 모으는 것에서 벗어난 짤줍자동화를 만끽할 수 있습니다.

## 1. 들어가기에 앞서서..
본 프로그램은 Danbooru API를 이용한 프로그램으로서 실행하기 위해서는 ID와 API Key 정보가 필요합니다.
회원가입 - My Account - API Key / View

확인한 정보를 본 code의 gAuth 변수에 입력해주면 준비 완료
또한 Python 3버전 이상에, requests 패키지가 설치되어 있어야 합니다(나머지는 기본이었나..?)
```
using cmd.exe(needs python bin path)

python -m pip install –upgrade pip
pip install requests
```

## 2. 실행
이 repository를 clone 받고 아무것도 수정하지 않은 상태에서는 계정 정보가 입력이 안되어 있기 때문에 당연히 실행이 안됩니다.
또한 원하는 이미지들을 검색하고 원하는 곳에 저장하기 위해서 다음의 항목들을 확인해줍시다.

1.  계정 정보: 위에서 설명한 것과 같이 Danbooru API를 이용하기 위해 필요합니다.
2.  keyword_d와 keyword_string: 원하는 작품의 폴더를 자동으로 생성하고 또한 이후에 하나의 배치파일로 여러개의 작품을 한번에 모으고 싶을 때를 위한 딕셔너리입니다. keyword_d에서는 단부루에서 검색하기 위한 keyword를 세팅하고, keyword_string에서는 저장할 폴더의 이름을 세팅합니다. 이 두 딕셔너리의 키의 이름을 어떻게 짓는지는 자유지만 **둘은 같은 키값을 공유해야 한다는 것이 중요**합니다.
3.  exdir와 copydir: 이미지를 저장하기 위한 경로를 설정합니다. 기본적으로는 keyword_string에서 설정한 이름의 폴더를 생성하도록 되어 있지만 원한다면 직접 폴더 경로를 지정해줄 수도 있습니다.

어느정도 세팅이 완료되면 IDE에서 실행해볼 수도 있고, cmd에서 `python non_recursive_collect.py helltaker`등의 명령어로 실행할 수 있습니다.

## 3. 코드 설명
### 3.1. 전체 개요
메인 함수가 실행되면 시스템의 인자값을 확인합니다.
```
    if len(sys.argv) > 1:
        setPath(sys.argv[1])
    else:
        setPath('helltaker')
```
IDE등에서 실행하게 되면 인자값이 없는 상태로 실행되는데 이 경우엔 기본적으로 helltaker 라는 키워드를 검색하게 됩니다.
이미지들을 저장할 디렉토리를 만들고 DailyLog 파일을 만들어 시작시간을 기록하고 업로드용 폴더의 파일들을 정리(삭제)한 뒤에 Main 메서드를 수행합니다.
Main 메서드가 모두 수행되면 DailyLog에 종료시각을 기록한 뒤에 프로그램이 종료됩니다.

### 3.2. Main 메서드
Main 메서드는 다음과 같은 루틴을 수행하도록 되어 있습니다.

-  파일들이 저장될 filedir 지정<br>
-  requests.get을 사용하기 위한 request format(페이지 주소) 생성, 검색<br>
Page Loop<br>
    -  페이지에 속한 이미지 목록 생성<br>
Image Loop<br>
        -  이미지 다운로드를 위한 request format(이미지 주소) 생성, 검색<br>
        -  중복된 이미지인지 검사 - 중복이라면 다음 이미지로 pass / 아니라면 다운로드 진행(+업로드용 폴더에 복사)<br>
Image Loop End<br>
    -  다음 페이지 주소로 검색<br>
    -  이미지 목록의 길이로 마지막 페이지인지 검사<br>
Page Loop End<br>
-  해당 키워드에 대한 전체 이미지, 저장된 이미지 갯수 출력

### 3.3. 여러가지 클래스, 메서드
#### 3.3.1. DownloadNum 클래스
DownloadNum 클래스에서는 해당 키워드에 대해 다운로드한 이미지 수를 초기화(init_dw_num)하고, 증가(increase_dw_num)시키며, 가져올 수(get_dw_num)도 있습니다.

#### 3.3.2. beepsound(times, freq, dur) 메서드
beepsound 메서드를 통해 times 횟수만큼 freq 주파수의 음을 dur의 길이만큼 생성할 수 있습니다. 보통 이 메서드를 통해서 현재 다운로드가 잘 진행되고 있는지 예외상황이 발생했는지, 프로그램이 종료되는지 청각적으로 확인할 수 있습니다.

#### 3.3.3. setDataStr(dataStr: list, page: int) 메서드
실제 Danbooru에 검색할 Data String을 만드는 메서드입니다.
```
def setDataStr(dataStr: list, page: int):
    dataStr.append('{ "post": { "tags": "')
    dataStr.append(keywords_value)
    dataStr.append('rating:safe" }, "page": ')
    dataStr.append(str(page))
    dataStr.append(' }')
    dataStr = ''.join(dataStr)

    return dataStr
```
keywords_value에는 위에서 설정했었던 keyword_d의 value 값이 들어가게 됩니다. 혹은 dataStr.append() 메서드를 수정해서 자신이 원하는 검색어로 수행할 수도 있습니다. 단, Danbooru에서는 Gelbooru와 달리 키워드 갯수 제한이 있다는 점에 주의해야 합니다(**Basic 유저는 2개, Gold 유저는 6개, Platinum 유저는 12개**).

#### 3.3.4. getSizeSTR(downloadPath: str) 메서드
파일 사이즈를 읽어서 킬로바이트 혹은 메가바이트 단위로 출력해줍니다.

#### 3.3.5. printProgress(iteration, total, prefix='', suffix='', decimals=1, barLength=100) 메서드
파일을 다운로드할 때 진행상황을 progress bar 형태로 출력해줍니다.

### 3.4. 기타
이미지를 다운로드하는 부분 밑에
```
# Copy to upload
# copyPath = os.path.join(copydir, filename)
# shutil.copy(downloadPath, copyPath)
```
로 주석처리되어 있는 부분이 있는데 만약 업로드용이나 일일모음등으로 따로 모아놓고 싶을 때 이 주석을 없애주면 이미지 다운로드와 동시에 복사가 수행됩니다.

또한 한번 처음부터 끝까지 돌리고 매일마다 같은 키워드를 모으고 싶을 때
```
# Use for daily Collecting
# if page > 5:
#     exit_flag = 0
#     fileDotArtist_txt.close()
#     break
```
이 부분의 주석을 없애주면 5페이지까지 검색하고 Main 메서드가 종료됩니다.
