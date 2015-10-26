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
function change(str){
	$("section").css("display","none");
	$("section#"+str).show();
}