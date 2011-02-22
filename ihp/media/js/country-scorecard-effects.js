jQuery(document).ready(function()
{
	jQuery('.infobox .item').hide();
	
	var openInfobox;
	
	jQuery('.infobox h2 a').click(function()
	{
		var toShow = jQuery(this).closest('.infobox').children('.item');
		
		if (!(toShow.data('shown')))
		{
			jQuery(toShow).slideToggle();
			
			if (openInfobox)
			{
				openInfobox.slideToggle();
			}
		}

		toShow.data('shown', true);
		
		if (openInfobox)
		{
			openInfobox.data('shown', false);
		}
		
		openInfobox = toShow;
		return false;
	});
			
	// add background images to items with curvy corners
	// if (jQuery.browser.msie && jQuery.browser.version < 9)
	{
		function moveProperty(property, from, to, replacement)
		{
			// alert(item.css('margin-top'));
			to.css(property, from.css(property));
			from.css(property, replacement);
		}
		
		function wrap(items, image_name_base)
		{
			items.each(function(i, obj)
			{
				var item = jQuery(obj);

				var outerWrap = jQuery('<div style="background: ' + 
					'url(' + images_path + '/' + image_name_base + '-top.png) ' +
					'no-repeat top; clear: both;">');

				var innerWrap = jQuery('<div style="background: ' +
					'url(' + images_path + '/' + image_name_base + '-bottom.png) ' +
					'no-repeat bottom;">');
				
				// moveProperty('border-left-style', item, outerWrap, 'none');
				moveProperty('border-style', item, outerWrap, 'none');
				moveProperty('border-color', item, outerWrap, 'inherit');
				moveProperty('border-width', item, outerWrap, '0');
				moveProperty('background-color', item, outerWrap, 'inherit');
				moveProperty('margin-bottom', item, outerWrap, '0');
				
				// alert(item.css('margin-top'));
				// outerWrap.css('margin', item.css('margin'));
				// item.css('margin', '0');

				item.wrap(outerWrap);
				item.wrap(innerWrap);
				item.after('<div style="clear: both;">');
			});
		}

		/*		
		wrap(jQuery('#scorecard h2').add('#scorecard h3'), 'scorecard-h2');
		wrap(jQuery('#scorecard .logos'), 'scorecard-item');
		*/
	} 
});
