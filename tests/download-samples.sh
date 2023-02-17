#!/bin/bash
rm -f tg-posts*.html tg-single-post*.html
id=0
function add () {
    local url=$1
    local url_type=$2
    id=$(($id + 1))
    if [ $url_type == 1 ];
    then
        curl $url -fo tg-posts-$id.html
    else
        curl "$url?embed=1&mode=tme" -fo tg-single-post-$id.html
    fi
}

add "https://t.me/s/evgenii_ponasenkov" 1
add "https://t.me/evgenii_ponasenkov/7561" 2
