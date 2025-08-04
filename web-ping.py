import requests 
import re
import csv
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime

class URLUploadTester:
    def __init__(self, timeout=10, max_workers=5):
        self.timeout = timeout
        self.max_workers = max_workers
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def check_url_exists(self, url):
        """Check if URL exists and is accessible"""
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://www.' + url
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            return {
                'url': url,
                'exists': True,
                'status_code': response.status_code,
                'final_url': response.url,
                'response_time': response.elapsed.total_seconds(),
                'error': None
            }
        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'exists': False,
                'status_code': None,
                'final_url': None,
                'response_time': None,
                'error': str(e)
            }
    
    def scan_for_upload_forms(self, url, html_content):
        """Scan HTML content for file upload forms"""
        upload_indicators = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for file input fields
            file_inputs = soup.find_all('input', {'type': 'file'})
            for input_field in file_inputs:
                form = input_field.find_parent('form')
                form_action = form.get('action', '') if form else ''
                upload_indicators.append({
                    'type': 'file_input',
                    'form_action': urljoin(url, form_action) if form_action else url,
                    'form_method': form.get('method', 'GET').upper() if form else 'GET',
                    'input_name': input_field.get('name', ''),
                    'input_accept': input_field.get('accept', ''),
                    'form_enctype': form.get('enctype', '') if form else ''
                })
            
            # Look for upload-related keywords in text and attributes
            upload_keywords = [
                'upload', 'file upload', 'choose file', 'select file', 
                'drop files', 'drag and drop', 'browse files', 'attach file'
            ]
            
            for keyword in upload_keywords:
                # Case-insensitive search in text content
                if re.search(keyword, soup.get_text(), re.IGNORECASE):
                    upload_indicators.append({
                        'type': 'keyword_match',
                        'keyword': keyword,
                        'context': 'text_content'
                    })
                
                # Search in element attributes
                elements_with_keyword = soup.find_all(attrs={
                    re.compile('.*'): re.compile(keyword, re.IGNORECASE)
                })
                for elem in elements_with_keyword:
                    upload_indicators.append({
                        'type': 'keyword_match',
                        'keyword': keyword,
                        'context': f'{elem.name} element attributes'
                    })
            
            # Look for drag-and-drop areas (common classes/ids)
            dropzone_selectors = [
                '[class*="dropzone"]', '[class*="drop-zone"]', '[class*="file-drop"]',
                '[id*="dropzone"]', '[id*="drop-zone"]', '[id*="file-drop"]'
            ]
            
            for selector in dropzone_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    upload_indicators.append({
                        'type': 'dropzone_area',
                        'element': elem.name,
                        'class': elem.get('class', []),
                        'id': elem.get('id', '')
                    })
            
            return upload_indicators
            
        except Exception as e:
            return [{'type': 'scan_error', 'error': str(e)}]
    
    def test_upload_endpoint(self, url):
        """Test if URL accepts file uploads by attempting a small test upload"""
        test_results = []
        
        # Common upload endpoints to try
        upload_paths = ['', '/upload', '/api/upload', '/file-upload', '/files']
        
        for path in upload_paths:
            test_url = urljoin(url, path)
            
            try:
                # Create a small test file
                test_file = {'file': ('test.txt', 'test content', 'text/plain')}
                
                # Try POST request
                response = self.session.post(
                    test_url, 
                    files=test_file, 
                    timeout=self.timeout,
                    allow_redirects=False
                )
                
                test_results.append({
                    'endpoint': test_url,
                    'method': 'POST',
                    'status_code': response.status_code,
                    'response_size': len(response.content),
                    'content_type': response.headers.get('content-type', ''),
                    'potentially_accepts_uploads': response.status_code not in [404, 405, 501]
                })
                
            except requests.exceptions.RequestException as e:
                test_results.append({
                    'endpoint': test_url,
                    'method': 'POST',
                    'error': str(e),
                    'potentially_accepts_uploads': False
                })
        
        return test_results
    
    def comprehensive_url_test(self, url):
        """Perform comprehensive test on a single URL"""
        print(f"Testing: {url}")
        
        # Check if URL exists
        existence_result = self.check_url_exists(url)
        
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'exists': existence_result['exists'],
            'status_code': existence_result['status_code'],
            'final_url': existence_result['final_url'],
            'response_time': existence_result['response_time'],
            'error': existence_result['error'],
            'upload_indicators': [],
            'upload_tests': []
        }
        
        if existence_result['exists'] and existence_result['status_code'] == 200:
            try:
                # Get page content for upload form scanning
                response = self.session.get(url, timeout=self.timeout)
                
                # Scan for upload forms
                upload_indicators = self.scan_for_upload_forms(url, response.text)
                result['upload_indicators'] = upload_indicators
                
                # Test upload endpoints
                upload_tests = self.test_upload_endpoint(url)
                result['upload_tests'] = upload_tests
                
            except Exception as e:
                result['scan_error'] = str(e)
        
        return result
    
    def test_urls_batch(self, urls):
        """Test multiple URLs concurrently"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self.comprehensive_url_test, url): url 
                for url in urls
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'url': url,
                        'error': f'Processing error: {str(e)}',
                        'exists': False
                    })
                
                # Small delay to be respectful to servers
                time.sleep(0.1)
        
        return results
    
    def export_results(self, results, format='json'):
        """Export results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            filename = f'url_test_results_{timestamp}.json'
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
        
        elif format == 'csv':
            filename = f'url_test_results_{timestamp}.csv'
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'URL', 'Exists', 'Status Code', 'Final URL', 'Response Time', 
                    'Has Upload Indicators', 'Upload Test Results', 'Error'
                ])
                
                # Write data
                for result in results:
                    writer.writerow([
                        result.get('url', ''),
                        result.get('exists', False),
                        result.get('status_code', ''),
                        result.get('final_url', ''),
                        result.get('response_time', ''),
                        len(result.get('upload_indicators', [])) > 0,
                        len([t for t in result.get('upload_tests', []) 
                            if t.get('potentially_accepts_uploads', False)]) > 0,
                        result.get('error', '')
                    ])
        
        print(f"Results exported to: {filename}")
        return filename

def load_urls_from_file(filename):
    """Load URLs from a text file"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'): # Skip empty lines and comments
                    urls.append(url)
        print(f"Loaded {len(urls)} URLs from {filename}")
        return urls
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return []
    except Exception as e:
        print(f"Error reading file '{filename}': {str(e)}")
        return []

def main():
    # Load URLs from file
    urls = load_urls_from_file('urls.txt')
    
    if not urls:
        print("No URLs to test. Please check your input file.")
        return
    
    # Show first few URLs for confirmation
    print(f"First few URLs to be tested:")
    for i, url in enumerate(urls[:5]):
        print(f" {i+1}. {url}")
    if len(urls) > 5:
        print(f" ... and {len(urls) - 5} more URLs")
    
    # Initialize tester
    tester = URLUploadTester(timeout=15, max_workers=3)
    
    print(f"Testing {len(urls)} URLs...")
    print("This may take a while depending on the number of URLs and their response times.")
    
    # Run tests
    results = tester.test_urls_batch(urls)
    
    # Print summary
    existing_urls = [r for r in results if r.get('exists', False)]
    urls_with_upload_indicators = [r for r in results if len(r.get('upload_indicators', [])) > 0]
    
    print(f"\n=== SUMMARY ===")
    print(f"Total URLs tested: {len(urls)}")
    print(f"Existing URLs: {len(existing_urls)}")
    print(f"URLs with upload indicators: {len(urls_with_upload_indicators)}")
    
    # Export results
    tester.export_results(results, 'json')
    tester.export_results(results, 'csv')
    
    # Print detailed results for URLs with upload potential
    print(f"\n=== URLS WITH UPLOAD POTENTIAL ===")
    for result in urls_with_upload_indicators:
        print(f"\nURL: {result['url']}")
        print(f"Status: {result['status_code']}")
        print(f"Upload indicators found: {len(result['upload_indicators'])}")
        for indicator in result['upload_indicators'][:3]: # Show first 3
            print(f" - {indicator}")

if __name__ == "__main__":
    main()
