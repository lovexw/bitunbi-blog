// 搜索功能 - 基于Hugo生成的JSON索引
(function() {
    var searchData = null;
    var searchInput = document.getElementById('search-input');
    var searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchResults) return;

    // 从URL参数读取初始搜索词
    var params = new URLSearchParams(window.location.search);
    var initialQuery = params.get('q');
    if (initialQuery) {
        searchInput.value = initialQuery;
    }

    function loadAndSearch(query) {
        if (!searchData) {
            searchResults.innerHTML = '<p class="search-loading">加载索引中...</p>';
            fetch('/index.json')
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    searchData = data;
                    performSearch(query);
                })
                .catch(function() {
                    searchResults.innerHTML = '<p class="search-error">索引加载失败，请刷新重试。</p>';
                });
        } else {
            performSearch(query);
        }
    }

    function performSearch(query) {
        query = query.trim().toLowerCase();
        
        if (!query) {
            searchResults.innerHTML = '<p class="search-hint">输入关键词开始搜索，共 ' + (searchData ? searchData.length : 0) + ' 篇文章</p>';
            return;
        }

        var results = [];
        for (var i = 0; i < searchData.length; i++) {
            var item = searchData[i];
            var title = (item.title || '').toLowerCase();
            var content = (item.content || '').toLowerCase();
            var summary = (item.summary || '').toLowerCase();
            var categories = (item.categories || []).join(' ').toLowerCase();

            var titleMatch = title.indexOf(query) !== -1;
            var contentMatch = content.indexOf(query) !== -1;
            var summaryMatch = summary.indexOf(query) !== -1;
            var categoryMatch = categories.indexOf(query) !== -1;

            if (titleMatch || contentMatch || summaryMatch || categoryMatch) {
                var score = 0;
                if (titleMatch) score += 10;
                if (summaryMatch) score += 5;
                if (categoryMatch) score += 3;
                if (contentMatch) score += 1;
                results.push({ item: item, score: score });
            }
        }

        results.sort(function(a, b) { return b.score - a.score; });

        if (results.length === 0) {
            searchResults.innerHTML = '<p class="search-empty">未找到包含 "' + escapeHtml(query) + '" 的文章</p>';
            return;
        }

        var html = '<p class="search-count">找到 ' + results.length + ' 篇相关文章</p>';
        html += '<div class="search-results-list">';
        
        // 只显示前50条
        var maxResults = Math.min(results.length, 50);
        for (var j = 0; j < maxResults; j++) {
            var item = results[j].item;
            html += '<a href="' + item.permalink + '" class="search-result-item">';
            html += '<div class="search-result-title">' + highlightKeyword(item.title, query) + '</div>';
            html += '<div class="search-result-meta">' + item.date;
            if (item.categories && item.categories.length > 0) {
                html += ' · ' + item.categories.join(' / ');
            }
            html += '</div>';
            if (item.summary) {
                html += '<div class="search-result-summary">' + highlightKeyword(truncateText(item.summary, 120), query) + '</div>';
            }
            html += '</a>';
        }
        
        if (results.length > 50) {
            html += '<p class="search-more">还有 ' + (results.length - 50) + ' 条结果未显示，请细化搜索关键词</p>';
        }
        
        html += '</div>';
        searchResults.innerHTML = html;
    }

    function highlightKeyword(text, keyword) {
        if (!text) return '';
        var escaped = escapeHtml(text);
        var regex = new RegExp('(' + escapeRegex(keyword) + ')', 'gi');
        return escaped.replace(regex, '<mark>$1</mark>');
    }

    function truncateText(text, maxLen) {
        if (text.length <= maxLen) return text;
        return text.substring(0, maxLen) + '...';
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function escapeRegex(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // 防抖
    var debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        var query = searchInput.value;
        debounceTimer = setTimeout(function() {
            loadAndSearch(query);
        }, 200);
    });

    // 初始搜索
    loadAndSearch(searchInput.value);
})();
