// Handle outline change on hand icon if clicked
$("a.like > i").on("click", handleLike);

async function handleLike(evt) {
    let question_id = evt.target.dataset.qid;

    if ($(evt.target).hasClass("far")) {
        console.log('No like - adding like now...');
        res = await axios.post(`/add_like/${question_id}`);
        if (res.statusText === 'OK') {
            $(evt.target).removeClass("far");
            $(evt.target).addClass("fas");
        };
        location.reload();
    } else if ($(evt.target).hasClass("fas")) {
        console.log('Already liked - removing like now...');
        res = await axios.post(`/remove_like/${question_id}`)
        if (res.statusText === 'OK') {
            $(evt.target).removeClass("fas");
            $(evt.target).addClass("far");
        };
        location.reload();
    }
}


// Handle modal
$('#exampleModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget) // Button that triggered the modal
    var recipient = button.data('whatever') // Extract info from data-* attributes
    // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
    // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
    var modal = $(this)
    modal.find('.modal-title').text('New message to ' + recipient)
    modal.find('.modal-body input').val(recipient)
  })

