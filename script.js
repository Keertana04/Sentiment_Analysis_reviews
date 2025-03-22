document.addEventListener('DOMContentLoaded', function() {
    const analyzeForm = document.getElementById('analyzeForm');
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const overallSummary = document.getElementById('overallSummary');
    const reviewTableBody = document.getElementById('reviewTableBody');
    const sentimentScoreCircle = document.getElementById('sentimentScoreCircle');
    const sentimentScoreValue = document.getElementById('sentimentScoreValue');
    const sentimentLabel = document.getElementById('sentimentLabel');
    
    let sentimentChart = null;
    let focusChart = null;
    
    analyzeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Show loading section
        loadingSection.classList.remove('d-none');
        resultsSection.classList.add('d-none');
        
        // Get form data
        const formData = new FormData(analyzeForm);
        const productUrl = formData.get('product_url');
        
        // Disable submit button
        const analyzeBtn = document.getElementById('analyzeBtn');
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        
        // Send request to server
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to analyze reviews');
                });
            }
            return response.json();
        })
        .then(data => {
            // Display results
            displayResults(data);
            
            // Hide loading, show results
            loadingSection.classList.add('d-none');
            resultsSection.classList.remove('d-none');
        })
        .catch(error => {
            // Show error
            alert('Error: ' + error.message);
            loadingSection.classList.add('d-none');
        })
        .finally(() => {
            // Re-enable submit button
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = 'Analyze Reviews';
        });
    });
    
    function displayResults(data) {
        // Display overall summary
        overallSummary.textContent = data.overall_summary;
        
        // Display overall sentiment score
        if (data.overall_sentiment_score !== undefined) {
            // Update the sentiment score circle
            const score = data.overall_sentiment_score;
            sentimentScoreValue.textContent = score;
            
            // Set the conic gradient based on the score
            sentimentScoreCircle.style.setProperty('--score', `${score}%`);
            
            // Update the sentiment label
            sentimentLabel.textContent = data.overall_sentiment || 'Neutral';
            
            // Add appropriate color class to the label
            sentimentLabel.className = 'sentiment-label';
            if (data.overall_sentiment) {
                const className = data.overall_sentiment.toLowerCase().replace(' ', '-');
                sentimentLabel.classList.add(className);
            }
        }
        
        // Clear previous table data
        reviewTableBody.innerHTML = '';
        
        // Add rows to the table
        data.detailed_analysis.forEach(review => {
            const row = document.createElement('tr');
            
            // Rating column
            const ratingCell = document.createElement('td');
            ratingCell.textContent = review.rating + ' ★';
            row.appendChild(ratingCell);
            
            // Sentiment column
            const sentimentCell = document.createElement('td');
            sentimentCell.textContent = review.sentiment;
            sentimentCell.classList.add(review.sentiment.toLowerCase() + '-sentiment');
            row.appendChild(sentimentCell);
            
            // Product related column
            const relatedCell = document.createElement('td');
            if (review.product_related) {
                relatedCell.textContent = 'Yes';
                relatedCell.classList.add('product-related');
            } else {
                relatedCell.textContent = 'No';
                relatedCell.classList.add('non-product-related');
            }
            row.appendChild(relatedCell);
            
            // Summary column
            const summaryCell = document.createElement('td');
            summaryCell.textContent = review.summary;
            summaryCell.classList.add('review-summary');
            row.appendChild(summaryCell);
            
            reviewTableBody.appendChild(row);
        });
        
        // Create charts
        createSentimentChart(data.sentiment_distribution);
        createFocusChart(data.product_related, data.non_product_related);
    }
    
    function createSentimentChart(distribution) {
        // Destroy previous chart if it exists
        if (sentimentChart) {
            sentimentChart.destroy();
        }
        
        const ctx = document.getElementById('sentimentChart').getContext('2d');
        sentimentChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Positive', 'Negative', 'Neutral'],
                datasets: [{
                    data: [
                        distribution.Positive,
                        distribution.Negative,
                        distribution.Neutral
                    ],
                    backgroundColor: [
                        '#28a745',  // green for positive
                        '#dc3545',  // red for negative
                        '#6c757d'   // gray for neutral
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    function createFocusChart(productRelated, nonProductRelated) {
        // Destroy previous chart if it exists
        if (focusChart) {
            focusChart.destroy();
        }
        
        const ctx = document.getElementById('focusChart').getContext('2d');
        focusChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Product Related', 'Non-Product Related'],
                datasets: [{
                    data: [productRelated, nonProductRelated],
                    backgroundColor: [
                        '#4285f4',  // blue for product
                        '#fd7e14'   // orange for non-product
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
});
