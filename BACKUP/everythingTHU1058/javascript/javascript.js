$(document).ready(function(){
    $("#facebook").click(function(){
        $(".TwitterPost").hide();
        $(".NewsPost").hide();
        $(".FacebookPost").show();
        $('#searchbar').hide();
    });
    $("#twitter").click(function(){
        $(".FacebookPost").hide();
        $(".NewsPost").hide();
        $(".TwitterPost").show();
        $('#searchbar').hide();
    });
    $("#news").click(function(){
        $(".FacebookPost").hide();
        $(".TwitterPost").hide();
        $(".NewsPost").show();
        $('#searchbar').show();
    });
    $("#home").click(function(){
        $(".FacebookPost").show();
        $(".TwitterPost").show();
        $(".NewsPost").show();
        $('#searchbar').hide();
    });
});
