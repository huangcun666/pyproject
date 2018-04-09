$(function () {
    $('.change').click(function () {
        var id=$(this).attr('id');
        var text=$(this).text();

        if(text=='完成') {
            $.get(
                'http://localhost:8888/todo/' + id + '/finish?status=yes',

                function (data) {
                    $("#"+id).prev().css('text-decoration','line-through');
                    $("#"+id).text('恢复');
                });


        }else{
            $.get(
                'http://localhost:8888/todo/' + id + '/finish?status=no',
                function (data) {
                    $("#"+id).prev().css('text-decoration','none');
                    $("#"+id).text('完成');
                });

        }
    }

    function getCookie(name) {
        var r = document.cookie.match("\\b"+name+"=([^:]*)\\b");
        return r ? r[1] : undefined;
    }
        $('.submit').click(function () {
            var title=$('.long_txt').val();
            $.post(
                'http://localhost:8888/todo/new',
                {
                    title: title,
                    _xsrf:getCookie("_xsrf")
                },
                function (data, status) {
                    $('.todos ul').append('<li><p class="title">'+title+'</p> &nbsp; ' +
                        '<a  style="cursor:pointer" class="change" id='+data["id"]+'>完成</a>' +
                        '<a href="/todo/"'+data["id"]+'/edit">修改</a></li>');
                }
            )
        })
