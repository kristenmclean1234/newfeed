$(document).ready(function(){
    $("#facebook").click(function(){
        $(".TwitterPost").hide();
        $(".NewsPost").hide();
        $(".FacebookPost").show();
    });
    $("#twitter").click(function(){
        $(".FacebookPost").hide();
        $(".NewsPost").hide();
        $(".TwitterPost").show();
    });
    $("#news").click(function(){
        $(".FacebookPost").hide();
        $(".TwitterPost").hide();
        $(".NewsPost").show();
    });
    $("#home").click(function(){
        $(".FacebookPost").show();
        $(".TwitterPost").show();
        $(".NewsPost").show();
    });
});
