$(document).ready(function() {
    document.session = $('#session').val();

    setTimeout(requestInventory, 100);

    $('#add-button').click(function(event) {
            $.post('//localhost:8000/cart',
                {
                    session:document.session,
                    action:'add'
                },function (data,status) {
                    $('#add-to-cart').hide();
                    $('#remove-from-cart').show();
                    $(event.target).removeAttr('disabled');
                })
    });

    $('#remove-button').click(function(event) {
        $.post('//localhost:8000/cart',
            {
                session:document.session,
                action:'remove'
            },function (data,status) {
                $('#remove-from-cart').hide();
                $('#add-to-cart').show();
                $(event.target).removeAttr('disabled');
            })
    });
});

function requestInventory() {
    var host='ws://localhost:8000/cart/status';
    var websocket=new WebSocket(host);
    websocket.onopen=function (evt){};
    websocket.onmessage=function (evt) {
        $('#count').html($.parseJSON(evt.data)['inventoryCount']);
    }
    websocket.onerror=function (evt){};


}