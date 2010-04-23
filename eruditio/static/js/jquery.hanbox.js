jQuery.hanbox_hide = function(div_id, link_id) {
	var target_div = jQuery("#" + div_id);
	var target_link = jQuery("#" + link_id);
	
	if (target_div.css('display') == 'block') {
		target_div.hide("slow");
	}
}

jQuery.hanbox_toggle = function(div_id, link_id, visible_text, hidden_text) {
	var target_div = jQuery("#" + div_id);
	var target_link = jQuery("#" + link_id);
	
	if (target_div.css('display') == 'block') {
		target_div.hide("slow");
		target_link.html(visible_text);
	} else {
		target_div.show("slow");
		target_link.html(hidden_text);
	}
}

jQuery.hanbox_toggle_img = function(div_id, link_id, visible_id, hidden_id) {
	var target_div = jQuery("#" + div_id);
	var target_link = jQuery("#" + link_id);
	var visible_image = jQuery("#" + visible_id);
	var hidden_image = jQuery("#" + hidden_id);
	
	if (target_div.css('display') == 'block') {
		target_div.hide("slow");
		hidden_image.hide();
		visible_image.show();
	} else {
		target_div.show("slow");
		visible_image.hide();
		hidden_image.show();
	}
}