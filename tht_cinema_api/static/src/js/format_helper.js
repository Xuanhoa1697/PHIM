odoo.define("tht_cinema_website.website_format_helper", function (require) {

    
    $(document).ready(function () {
        $('.format_date_ddmmyyyy').each(function(index){
            let thu = ['CN','Hai','Ba','Tư','Năm','Sáu','Bảy']
            let css_thu = '' , css_ngay =''; 
            // $(this).html('abc')
            let res = ''
            if ($(this).html() !='') {
                res = $(this).html().substr(7,2) + '/' + $(this).html().substr(5,2) + '/' + $(this).html().substr(0,4)
            }
            date_val = $(this).html()
            date_result = `${date_val.substr(0,4)},${date_val.substr(5,2)},${date_val.substr(8,2)}`
            date = new Date(date_result);
            thu_i = date.getDay();


            // index==0 ? css_thu= 'css_thu0' : css_thu='css_thu1'
            switch(thu_i) {
                case 0:
                    css_thu= 'css_thu0' 
                  break;
                case 6:
                    css_thu= 'css_thu6' 
                  break;
                default:
                  // code block
              }

            index==0 ? css_ngay= 'css_ngay0' : css_ngay='css_ngay1'

            // index==0 ? thang=`<div class='css_month'>Tháng ${date.getMonth()}/${date.getFullYear()} </div>` : thang=''
                       
            $(this).html(`<div class='css_thu ${css_thu}' > ${thu[thu_i]} </div> <div class='css_ngay ${css_ngay}'> ${date.getDate()} </div>`)
        })

        $('.date_ddmmyyyy').each(function(index){
          
            // $(this).html('abc')
            let res = ''
            if ($(this).html() !='') {
                res = $(this).html().substr(8,2) + '/' + $(this).html().substr(5,2) + '/' + $(this).html().substr(0,4)
            }
                       
            $(this).html(res)
        })

        $('.thangchieu').each(function(index){
            let res = ''
            
            if ($(this).html() !='') {
                res = $(this).html()
                console.log(res);
                // res =  $(this).html().substr(4,2) + '/' + $(this).html().substr(0,5)
                $(this).html('Tháng '+$(this).html().substr(6,2)+'/'+$(this).html().substr(1,4))
            }
                       
            
        })
        
    })
 
   

})