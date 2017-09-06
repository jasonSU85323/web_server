/*
作者：hsu po-wei
E-Mail：hpw925@hotmail.com
授權：GPL 3
*/

(function(jQuery){
		  
	jQuery.fn.tablepage = function(oObj, dCountOfPage) {

		var dPageIndex = 1;
		var dNowIndex = 1;
		var sPageStr = "";
		var dCount = 0;
		var oSource = jQuery(this);
		var sNoSelColor = "#CCCCCC";
		var sSelColor = "black";
		var sFontColor = "white";

 		change_page_content();

		function change_page_content()
		{
			//取得資料筆數
			dCount = oSource.children().children().length - 1;

			//顯示頁碼
			sPageStr = "<table><tr><td style='padding: 5px;height:30px;'><b>第</b></td>";
			
			dPageIndex = 1;
			
			for (var i = 1; i <= dCount; i += dCountOfPage)
			{
				if (dNowIndex == dPageIndex)
				{
					sPageStr += "<td style='padding: 4px' valign='top'><table style='width:20px;height:20px;cursor:pointer;color:" + sFontColor + ";border-collapse:collapse;border-style:solid;border-width:1px;border-color:" + sSelColor + ";background-color:" + sSelColor + "'><tr><th style='text-align:center;'>" + (dPageIndex++) + "</th></tr></table></td>";
				}
				else
				{
					sPageStr += "<td style='padding: 4px'valign='top'><table style='width:20px;height:20px;cursor:pointer;color:" + sFontColor + ";border-collapse:collapse;border-style:solid;border-width:1px;border-color:" + sNoSelColor + ";background-color:" + sNoSelColor + "'><tr><th style='text-align:center;'>" + (dPageIndex++) + "</th></tr></table></td>";
				}
			}
			
			sPageStr += "<td style='padding: 5px;height:30px;'><b>頁</b></td></tr></table>";
			
			oObj.html(sPageStr);
			
			dPageIndex = 1;
			
			//過濾表格內容
			oSource.children().children("tr").each( function () {
			
				if (dPageIndex <= (((dNowIndex - 1) * dCountOfPage) + 1) || dPageIndex > ((dNowIndex * dCountOfPage) + 1))
				{
					jQuery(this).hide();
				}
				else
				{
					jQuery(this).show();	
				}
				
				dPageIndex++;
			});
			
			oSource.children().children("tr").first().show(); //head一定要顯示
						
			//加入換頁事件
			oObj.children().children().children().children().each( function () {
		
				jQuery(this).click( function () {
				
					dNowIndex = jQuery(this).find("tr").text();
					
					if (dNowIndex > 0)
					{
						change_page_content();
					}
				});
			});
		}
	};
})(jQuery);


