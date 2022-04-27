$(document).ready(function () {
    $('#id_register_form_button').on('click',function(e){
        if (e.ctrlKey || e.metaKey) {
            $('#id_ctrl_flag').val("1")
        } else {
            $('#id_ctrl_flag').val("0")
        }
        $('#signup_form').submit();
    });
});
