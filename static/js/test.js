/**
 *  ACTIVE
 */
$(document).ready(function() {
	$('.navbar .standard_li').click(function(e) {
	});
	$("#side_menu li").click(function(){
		$("#side_menu .active").removeAttr("class");
		$(this).attr("class", "active");
	});
	$("#side_menu li").mouseover(function(){
	});
	$("#side_menu li").mouseout(function(){
		$(this).css("font-weight", "normal")
	});
	$(".navbar .navbar-inner  .standard_li > a").mouseover(function(){
		$(this).css("background-color", "#000")
		$(this).css("color", "#fff")
	});
	$(".navbar .navbar-inner  .standard_li > a").mouseout(function(){
		if($(this).attr("class") != "active")
			$(this).css("background-color", "#222");
	});
	$(".dropdown2").mouseover(function(){
		$(".dropdown-menu2").show()
	});
	$(".dropdown2").mouseout(function(){
		$(".dropdown-menu2").hide()
	});
	$(".dropdown2 li a").mouseover(function(){
		$(this).css("text-decoration", "underline")
	});
	$(".dropdown2 li a").mouseout(function(){
		$(this).css("text-decoration", "none")
	});
	$(".dropdown-submenu").click(function(){
		$(".fee_sub").show();
	})
});
function getProducts(offset){
	$("#more").remove();
    $.ajax({
      type: "POST",
      url: "/getProducts",
      dataType: 'html',
      data: JSON.stringify({ "offset": offset})
    })
    .done(function( data ) { // check why I use done
    	$(".product").last().append(data);
    });
};
function deleteProduct(date){
	if(confirm("삭제하시겠습니까?")){	
		$("[name='key']").val(date);
		deleteForm.submit();
	}
}
function deleteContent(key){
	if(confirm("삭제하시겠습니까?")){	
		$("[name='key']").val(key);
		deleteForm.submit();
	}
}
function change(str){
	$("section").css("display","none");
	$(str).show();
}
function changeMenuColor(str){
	$("."+str).css("background-color", "#000")
	$("."+str).attr("class", "active");
	if(location.hash)
		change(location.hash);
}
window.addEventListener('hashchange', function(){
	change(location.hash);
});
function goRepair(){
	location.href = "description#repair";
}