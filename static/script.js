(() => {
  const articleRecommendationForm = document.querySelector('#articleRecommendationForm')
  const resultsContainer = document.querySelector('#resultsContainer')
  const resultsTableBody = document.querySelector('#resultsTableBody')

  articleRecommendationForm.addEventListener('submit', event => {
    event.preventDefault()

    resultsContainer.style.display = 'none'

    const selectedArticles = Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(item => item.value)

    fetch(`/api/search?history=${selectedArticles.join(',')}`)
      .then(response => response.json())
      .then(data => {
        const tableBodyContent = data.reduce((output, item) => {
          output += `<tr><td class="titleColumn">${item.title}</td><td class="publicationColumn">${item.publication}</td><td class="scoreColumn">${(item.score * 100).toFixed(2)}%</td></tr>`
          return output
        }, '')

        resultsTableBody.innerHTML = tableBodyContent
        resultsContainer.style.display = 'block'
      })
      .catch(() => {
        alert('Whoops! Something went wrong while searching.')
      })
  })
})()
