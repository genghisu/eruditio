(function($){
jQuery.AjaxDefaults = {  
	event:'click',
	link:false, 
	target:'#container',
	method: 'GET',
	effect:'fade',
	loading_txt:'',
	loading_img:"/media/img/ajax/loading.gif",
	loading_target: false,
	loading_div: 'large_loading_div',
	forms:false,
	onStart:function(op){}, 
	onError:function(op){},
	onSuccess:function(op){},
	onComplete:function(op){}
};

jQuery.ajax_start = function(container_id) {
	var opts = jQuery.extend({},jQuery.AjaxDefaults);
	var container = jQuery("#" + container_id);
	var img_html = "<div id='"+opts.loading_div+"'><img src='"+opts.loading_img+"' alt='Loading...' title='Loading...' ></div>";
	container.html(img_html);
	var top_left = jQuery.center_element(container_id, opts.loading_div);
	jQuery("#" + opts.loading_div).css("display", "block").css("top", top_left.top).css("left", top_left.left);
	return;
};

jQuery.fn.ajax_update = function(options) {
	var opts = jQuery.extend({action: 'click'},jQuery.AjaxDefaults, options);
	var metadata = jQuery(this).metadata({type:'attr', name:'data'});
	var target = metadata.target;
	var link = metadata.link;
	
	if (opts.action == 'click') {
		this.each(function() {
			jQuery(this).bind("click",function() {
				if (opts.effect == 'none') {
				} else {
				    jQuery("#" + target).fadeOut("slow");
				}
				$.ajax({
            				url: link,
            				cache: false, 
            				success: function(html) {
					jQuery("#" + target).html(html);
				}
    				});
			    if (opts.effect == 'none') {
	    	    } else {
					jQuery("#" + target).fadeIn("slow");
			    }
				return false;
			});
		});
	} else if (opts.action == 'keyup') {
		this.each(function() {
			jQuery(this).bind("keyup",function() {
				var data = encodeURIComponent('_' + jQuery(this).val() + '_');
				$.ajax({
            				url: link + data,
            				cache: false, 
            				success: function(html) {
					jQuery("#" + target).html(html);
				}
    				});
				return false;
			});
		});
	} else {
		this.each(function() {
			jQuery(this).bind("click",function() {
				jQuery("#" + target).fadeOut("slow");
				$.ajax({
            				url: link,
            				cache: false, 
            				success: function(html) {
					jQuery("#" + target).html(html);
				}
    				});
				jQuery("#" + target).fadeIn("slow");
				return false;
			});
		});
	}
};
})(jQuery);
