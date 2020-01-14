$(document).ready(function(){

	$('#old_pass').blur(function(){
		var value=$(this).val();
		alert("wow");
		console.log("dsfdjsjfdkdsjfksj");
		if(value.length==0){
			$('#error_oldpass').text('Please fill this current password field');
		}else{$('#error_oldpass').text('');}
		});
	
	$('#new_pass').blur(function(){
		var value=$(this).val();
		if(value.length==0){
			$('#error_newpass').text('Please fill this new password field');
		}else{$('#error_newpass').text('');}
		});

	$('#con_pass').blur(function(){
		var value=$(this).val();
		if(value.length==0){
			$('#error_conpass').text('Please fill this confirm password field');
		}else{$('#error_conpass').text('');}
		});

});