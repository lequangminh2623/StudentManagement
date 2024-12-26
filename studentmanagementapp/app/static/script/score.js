window.onload = function() {
    const exportButton = document.getElementById('export-button');
    exportButton.addEventListener('click', function() {
        const transcriptId = this.dataset.transcriptId;
        window.location.href = `/transcripts/${transcriptId}/export`;
    });
}