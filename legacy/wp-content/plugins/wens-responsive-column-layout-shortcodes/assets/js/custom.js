/**
*
* JQuery remove unncessary <p></p> tag from the colum layout div
*
*/

jQuery(document).ready(function(){
        $ = jQuery;
   $('p').filter(function(e){  
       
       if($(this).html()==""){
        $(this).remove();  
    	} 
    });
    $('p').each(function() {
    var $this = $(this);
    if($this.html().replace(/\s|&nbsp;/g, '').length == 0)
        $this.remove();
});
});
