
$(document).ready(function() {
	$('#addskate-container').hide();
	$('.submitbtn-progress').hide();
	$('.comment-progress').hide();
    $('#close').click(function() {
    	$('#addskate-container').slideUp();
    });
    
	// add click action to the add-skate button
    $('.add-btn').click(function() {
        $('#addskate-container').slideDown();
    	$('#size').val($('#size-slider').slider("value"));
    	$('#price').val("FREE!");
      });
    
    // add click binding to the reserve buttons
    $('.action-btn').bind('click',function() {
    	$(this).prev().show();
		if( $(this).hasClass('delete-btn')) { 
			var $url = "/skate/delete";
		    var $msg = "This will permenantly delete these skates. Continue?";
		    var $buttontext = "It's gone!"
	    } else {
			var $url = "/skate/checkout";
			var $msg = "This will initiate an email to the owner. Continue?";
			var $buttontext = "Request submitted!";
	    }
		
    	c = window.confirm($msg);
		if(c) {
    		var button = $(this);
    		$.ajax({
    			type: "POST",
    			data: "key="+$(this).attr('skateid'),
    			url: $url,
    			error: function(msg) {
                    alert("hmph. something failed. please try again later.");
                    $(button).prev().hide();
                },
    			success: function(msg) {
                	//alert("it worked!");
                	if( $(button).hasClass('delete-btn') )
                		$(button).parent().parent().slideUp("slow");
                	else
                		$(button).html($buttontext);
        		        $(button).removeClass('action-btin');
                        $('.submitbtn-progress').hide();
                }
    		});
    	} else
    		$(this).prev().hide();
    });
    
	$(':input','#myform')
	 .not(':button, :submit, :reset, :hidden')
	 .val('')
	 .removeAttr('checked')
	 .removeAttr('selected');

	// initialize the sliders in the add-skate form
    // skate size...
	$('#size-slider').slider({
		value: 5,
		range: "min",
		step: 0.5,
		min: 1,
		max: 15,
		slide: function(event,ui) {
		    $("#size").val(ui.value);
	    }
	});
	$('#size').val($('#size-slider').slider("value"));
    // skate price...
	$('#price-slider').slider({
		value: 0,
		step: 1,
		min: 0,
		max: 50,
		slide: function(event,ui) {
		    if( ui.value == '0' )
		    	$("#price").val("FREE!");
		    else
  		        $("#price").val(ui.value);
	    }
	});
	$('#price').val("FREE!");

	
	var newSkateOptions = { 
            target:        '#output2',   // target element(s) to be updated with server response 
            beforeSubmit:  showRequest,  // pre-submit callback 
            success:       showResponse,  // post-submit callback 
     
            url: '/addskate',         // override for form's 'action' attribute 
            type: 'post',        // 'get' or 'post', override for form's 'method' attribute 
            dataType:  'json',        // 'xml', 'script', or 'json' (expected server response type) 
            clearForm: true,        // clear all form fields after successful submit 

            // other available options: 
            resetForm: true        // reset the form after successful submit 
     
            // $.ajax options can be used here too, for example: 
            //timeout:   3000 
        }; 
     
     // bind to the form's submit event 
     $('.addskate-form').submit(function() { 
          // inside event callbacks 'this' is the DOM element so we first 
          // wrap it in a jQuery object and then invoke ajaxSubmit 
          $(this).ajaxSubmit(newSkateOptions); 
     
          // !!! Important !!! 
          // always return false to prevent standard browser submit and page navigation 
          return false; 
     }); 
     
     
     var newComment = {
    		 beforeSubmit: preSubmitComment,
    		 success: postSubmitComment,
    		 url: '/addcomment',
    		 type: 'post',
    		 dataType: 'json',
    		 clearFrom: true,
    		 resetForm: true,
     };
     $('#addcomment-form').submit(function() {
    	 $(this).ajaxSubmit(newComment);
    	 return false;
     });
     
}); // ready function

// pre-submit callback 
function showRequest(formData, jqForm, options) {

    // formData is an array; here we use $.param to convert it to a string to display it 
    // but the form plugin does this for you automatically when it submits the data 
    var queryString = $.param(formData); 
    //alert('About to submit: \n\n' + queryString); 
	$('.submitbtn-progress').show();
	// here we could return false to prevent the form from being submitted; 
    // returning anything other than false will allow the form submit to continue 
    return true; 
} 
 
// post-submit callback 
function showResponse(skate, statusText, xhr, $form)  { 
    // if the ajaxSubmit method was passed an Options Object with the dataType 
    // property set to 'json' then the first argument to the success callback 
	// is the json data object returned by the server
	$('.comment-progress').hide();
	$("#addskate-container").slideUp();
	$("#inventory #skate:first").before(
			"<div id='skate'>" +
			"<img class='photo' src="+skate.picture+"></img>" +
			"<div id='details'>" +
			"<span class='owner'>"+skate.owner+"</span>" +
			"<hr/>" +
			"<table>" +
			 "<th>size</th><th> </th><th>price</th>" +
			 "<tr>" +
			  "<td>"+skate.size+"</td>" +
			  "<td> </td>" +
			  "<td class='"+skate.priceStyle+"'>"+skate.price+"</td>" +
			 "</tr>" +
			"</table>" +
			"<span class='note'>"+skate.note+"</span>" +
			"</div>" +
			"</div>");

}

function preSubmitComment(formData, jqForm, options) {
    var queryString = $.param(formData); 
	$('.comment-progress').show();
    return true; 
}
//post-submit callback 
function postSubmitComment(comment, statusText, xhr, $form)  { 
    // if the ajaxSubmit method was passed an Options Object with the dataType 
    // property set to 'json' then the first argument to the success callback 
	// is the json data object returned by the server
	$('.comment-progress').hide();
	$("#event-container #event:first").before(
			"<div id='event'>"+
			"<div id='event-pic'>"+comment.profilePic+"</div>" +
			"<div id='event-body'>"+comment.body+"</div>" +
			"</div>");
}
// Facebook account logout...
function fbLogout() {
	FB.logout(function(response) {
		window.location.href='/';
	});
}
