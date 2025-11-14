/**
 * TaskComment functionality
 *
 */

(function(ux){

    // To display errors 
    var	pageError = function(errObject) {
            ux.dialog.alert( errObject.FRIENDLY + '<br>' + errObject.MESSAGE );
        },
		onUpdatedCallback = function(updatedComments){};

			
	function initModal(modalTmpl, modalID, patienttaskkey, comment)
	{
		var data = {
			'ModalId'			: modalID,								//modal id
			'CommentId' 		: "modal-comments-" + patienttaskkey,	//textarea id
			'ModalHiddenId'		: "modal-hidden-" + patienttaskkey,		//hidden id
			'ModalCancelId'		: "cancel-" + modalID,					//modal cancel id
			'ModalSaveId'		: "save-" + modalID,					//modal save id
			'TaskKeyList'		: patienttaskkey,						//hidden value
			'CommentText'		: comment								//current commment
		};

		return modalTmpl.render(data);
	}
				
	//retrieve comment
	function getTaskComment(patienttaskkey, originalComment, modalTmpl) {
		var commentPlaceHolder = '#comment-' + patienttaskkey;
		load(patienttaskkey, originalComment, commentPlaceHolder, modalTmpl);
	} 
	
	function load(patienttaskkey, taskComment, commentPlaceHolder, modalTmpl) {
		applyClass(patienttaskkey, taskComment, commentPlaceHolder);


		if(taskComment.length > 0)
		{
			applyHover(patienttaskkey, taskComment, commentPlaceHolder);
			$(commentPlaceHolder).tooltip('enable');
		}
		else 
		{
			$(commentPlaceHolder).tooltip('disable');
		}

		applyModal(patienttaskkey, taskComment, commentPlaceHolder, modalTmpl);
	}
	
	function clear(commentPlaceHolder) {
		var modalID = 'modal' + commentPlaceHolder.replace('#comment-', '');
		$(commentPlaceHolder).removeClass('kicon-comment kicon-comment-add');
		$(commentPlaceHolder).empty();

		// Remove any old instance of the modal
		while ( $('#' + modalID).length > 0 ) {
			$('#' + modalID).remove();
		} 
	}
	
	function applyClass(patienttaskkey, comment, commentPlaceHolder) {
		//use the correct class(icon) when we have a comment
		$(commentPlaceHolder).toggleClass((comment.length > 0 ? 'kicon-comment' : 'kicon-comment-add'), true);
	}
	
	function applyHover(patienttaskkey, comment, commentPlaceHolder) {
			// Remove the previous tooltip
			$(commentPlaceHolder).data('tooltip', false);
			$(commentPlaceHolder).prop('data-placement', 'left')
				.prop('title', comment.replace(/\n/g,""))
				.tooltip();
	}
	
	function applyModal(patienttaskkey, comment, commentPlaceHolder, modalTmpl) {	
		//add modal markup with comment			
		var modalID = 'modal' + patienttaskkey;
        var modalBodyInstance = initModal(modalTmpl, modalID, patienttaskkey, comment);
		
		$(commentPlaceHolder).append(modalBodyInstance);
		
		$('#' + modalID).appendTo($('body')); // fixes modal getting bad z-index

		// Store button text to disable it during process
		var $actionButtons = $('#' + modalID + ' .modal-footer .btn');
        $actionButtons.each(function(i, elem){
        	if( ! $(elem).data('defaultValue') )
            	$(elem).data('defaultValue', $(elem).val());
        });
				
		//open modal
		var commentAtOpen;
		$(commentPlaceHolder).click( function() {
			commentAtOpen = $('#modal-comments-' + patienttaskkey).val();

            $actionButtons.each(function(i, elem){
                $(elem).val($(elem).data('defaultValue')).removeAttr('disabled');
            });

			$('#' + modalID)
				.on('shown', function(){ 
					$('textarea:first', $('#' + modalID)).focusToEnd();
					})
				.modal('show');
		});
		
		//close modal
		$('#cancel-' + modalID).on('click', function() {
            $actionButtons.val('Please Wait').attr('disabled', 'disabled');
			// reset comment
			$('#modal-comments-' + patienttaskkey).val(commentAtOpen);
			$('#' + modalID).modal('hide');
			return false;
		});
		
		//save + close modal
		$('#save-' + modalID).on('click', function() {
            $actionButtons.val('Please Wait').attr('disabled', 'disabled');
			var modalPatienttaskkey = $('#modal-hidden-' + patienttaskkey).val();
			var modalTaskComment = $('#modal-comments-' + patienttaskkey).val();
			saveTaskComment(modalPatienttaskkey, modalTaskComment, modalTmpl);
			return false;		
		});	
	}
	
	//save comment
	function saveTaskComment(patienttaskkey, taskComment, modalTmpl) {
		$.ajax({
			type: 'GET',
			dataType: 'json',
			url: '/AM/Patient/TaskDetail/TaskDetailProxy.cfc',
			data: {
				method: 'setTaskComment',
				fpatienttaskkey: patienttaskkey,
				taskComment: taskComment
			},
			success: function(resultStruct){		
				if(resultStruct.result === "success"){
					var patienttaskkey = resultStruct.commentPlaceHolder;
					var taskComment = resultStruct.taskComment;
					var modalID = 'modal' + patienttaskkey;
					var commentPlaceHolder = '#comment-' + patienttaskkey;
					$('#' + modalID).modal('hide');
					clear(commentPlaceHolder);
					load(patienttaskkey, taskComment, commentPlaceHolder, modalTmpl); 

					var updatedComments = [{'patienttaskkey': patienttaskkey, 'comment': taskComment}];
					if( $.isFunction(onUpdatedCallback) ) onUpdatedCallback( updatedComments );
				}
				else{
					var patienttaskkey = resultStruct.commentPlaceHolder;
					var modalID = 'modal' + patienttaskkey;
					$('#cancel-' + modalID).trigger('click');
					ux.dialog.alert( 'Your comment could not be saved at this time, please try again later.' );
				}
			},
			error: function(xhr, textStatus, errorThrown) {
				ux.dialog.alert('Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText);
			}
		});
	}
	var localTaskComment  = function($elems, onUpdated){
			/* Verify an empty collection wasn't passed */
			if ( !$elems.length ) {
				return $elems;
			}
			onUpdatedCallback = onUpdated;

			if( $.render.taskCommentTmpl ){
				//wire up all $elems passed in
				$elems.each(function(){
					var $elem = $(this);
					// exit if the it was initizalized on the element
					if( $elem.data('ux-taskcomment') ) return;
					var elemTwoTaskKey = $elem.attr('id').split('-')[1];
					var originalComment = $elem.prop('title');
					$elem.prop('');
					getTaskComment(elemTwoTaskKey, originalComment, $.templates.taskCommentTmpl);	
					// mark element as initialized	
					$elem.data('ux-taskcomment', true);
				});
			} else {
				//get modal markup
				$.ajax({
				    url : "/AM/assets/js/ux/view/taskComment.html",
				    success : function(result){
				    	$.templates({ taskCommentTmpl: result });
						//wire up all $elems passed in
						$elems.each(function(){
							var $elem = $(this);
							// exit if the it was initizalized on the element
							if( $elem.data('ux-taskcomment') ) return;
							var elemTwoTaskKey = $elem.attr('id').split('-')[1];
							var originalComment = $elem.prop('title');
							$elem.prop('');
							getTaskComment(elemTwoTaskKey, originalComment, $.templates.taskCommentTmpl);	
							// mark element as initialized	
							$elem.data('ux-taskcomment', true);		
						});
				    },
					error: function(xhr, textStatus, errorThrown) {
						ux.dialog.alert('Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText);
					}
				});	
			}
				
		}



		// Get task
		$.extend( localTaskComment, { multiappend: function(taskKeyList, $commentDOMElements, onComplete, onUpdateRow){ 


					var initMultiAppend = function(modalTmpl){
											
						var data = {
							'ModalId'			: "comment-multiappend",			//modal id
							'CommentId' 		: "modal-multiappend-comments",		//textarea id
							'ModalHiddenId'		: "modal-hidden-multiappend",		//hidden id
							'ModalCancelId'		: "cancel-multiappend",				//modal cancel id
							'ModalSaveId'		: "save-comment-multiappend",		//modal save id
							'TaskKeyList'		: taskKeyList,						//hidden value
							'CommentText'		: ''								//current commment
						};

						var modalBody = modalTmpl.render(data);				
			
						$('body').append(modalBody);
						
											
						//close modal
						$('#cancel-multiappend').on('click', function() {
           					$(this).parent().find('.btn').val('Please Wait').attr('disabled', 'disabled');
							$('#comment-multiappend').modal('hide');
							$('div').remove('#comment-multiappend');
							if( $.isFunction(onComplete) ) onComplete.call();
							return false;
						});
						
						//save + close modal
						$('#save-comment-multiappend').on('click', function() {
            				$(this).parent().find('.btn').val('Please Wait').attr('disabled', 'disabled');
							var modalPatienttaskkeylist = $('#modal-hidden-multiappend').val();
							var modalTaskCommentappend = $('#modal-multiappend-comments').val();
							
							$.ajax({
								type: 'GET',
								dataType: 'json',
								url: '/AM/Patient/TaskDetail/TaskDetailProxy.cfc',
								data: {
									method: 'multiTaskCommentAppend',
									fpatienttaskkeylist: modalPatienttaskkeylist,
									appendComment: modalTaskCommentappend
								},
								success: function(resultStruct){		
									if(resultStruct.result === "success"){

										$commentDOMElements.each(function(i, elem){
											var currentComment = $(elem).attr('data-original-title'),
												commentPlaceHolder = '#' + $(elem).attr('id'),
												patienttaskkey = commentPlaceHolder.match(/[0-9]+/)[0],
												taskComment = ($('#modal-comments-' + patienttaskkey).val() ? $('#modal-comments-' + patienttaskkey).val() + "\n" : '') + modalTaskCommentappend;
										// $.each(modalPatienttaskkeylist.split(','), function(i, patienttaskkey){
										// 	var elem = $( '#' + patienttaskkey ),
										// 		currentComment = $(elem).attr('data-original-title'),
										// 		commentPlaceHolder = '#' + patienttaskkey,
										// 		patienttaskkey = commentPlaceHolder.match(/[0-9]+/)[0],
										// 		taskComment = ($('#modal-comments-' + patienttaskkey).val() ? $('#modal-comments-' + patienttaskkey).val() + "\n" : '') + modalTaskCommentappend;

											$(elem).removeAttr('data-original-title');
											$(elem).attr('title', taskComment);
											clear(commentPlaceHolder);
											load(patienttaskkey, taskComment, commentPlaceHolder, $.templates.taskCommentTmpl);

											
										});
										if( $.isFunction(onUpdateRow) ) onUpdateRow( modalTaskCommentappend );

										$('#comment-multiappend').modal('hide');
										$('div').remove('#comment-multiappend');	 
									}
									else{
										$('#cancel-multiappend').trigger('click');
										ux.dialog.alert( 'Your comment could not be saved at this time, please try again later.' );
									}
								},
								error: function(xhr, textStatus, errorThrown) {
									ux.dialog.alert('Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText);
								}
							});	
							if( $.isFunction(onComplete) ) onComplete.call();	
							return false;
						});	
						
						$('#comment-multiappend')
							.on('shown', function(){ 
								$('textarea:first', $('#comment-multiappend')).focusToEnd();
								})
							.modal('show');
					}

					if( $.render.taskCommentTmpl  ){
						initMultiAppend( $.templates.taskCommentTmpl );
					} else {
						$.ajax({
						    url : "/AM/assets/js/ux/view/taskComment.html",
						    success : function(result){
				    			$.templates({ taskCommentTmpl: result });
						        initMultiAppend($.templates.taskCommentTmpl );
						    },
							error: function(xhr, textStatus, errorThrown) {
								ux.dialog.alert('Status Returned: ' + textStatus + '<br>Description: ' + xhr.statusText);
							}
						});
					}

				}
			}
		);
	var extendUX = function(){
		$.extend( ux, {
			/** @lends ux */

			/**
			 * <p>Initializes TaskComment on the given $elems.</p>
			 *
			 * <p>When loading this library the taskComment
			 * will be applied to all the div fields with ux-taskComment.
			 * So if you want to apply the taskComment to a div field you
			 * only need to output something like this:</p>
			 * <pre>
			 * &lt;div type="text" id="[patienttaskkey]" name="[patienttaskkey]" class="ux-taskcomment"&gt; &lt;div/&gt;
			 * </pre>
			 *
			 * <b>Remember:</b> The taskComment will be looking for the patienttaskkey as the div id.
			 *
			 * @author Michael Leduc (michael.leduc@kinnser.com)
			 */
			 taskComment:localTaskComment 

		});
		// Initializes taskComment automatically
		$(document).ready(function(){ ux.taskComment($("div.ux-taskcomment")); });

	}
	
	extendUX();
	
})(ux);