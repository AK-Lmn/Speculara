import unittest
import httpx
from backend.main import app

class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test')
    async def asyncTearDown(self): await self.client.aclose()
    async def test_upload_returns_real_totals_without_cache(self):
        r=await self.client.post('/api/analyze',content=b'views,sales\n100,2\n',headers={'X-Filename':'posts.csv','Content-Type':'application/octet-stream'})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['totals']['sales'],2)
        self.assertEqual(r.json()['schema_version'],2)
        self.assertEqual(r.json()['ratios']['sales_per_view']['percent'],2)
        self.assertIsNone(r.json()['ratios']['saves_per_view']['percent'])
        self.assertNotIn('NaN',r.text)
        self.assertNotIn('Infinity',r.text)
        self.assertEqual(r.headers['cache-control'],'no-store')
    async def test_rejects_malformed_empty_and_oversized_files(self):
        for content,name in [(b'', 'posts.csv'),(b'a,b\n1,2\n','posts.csv'),(b'junk','posts.xlsx'),(b'views\n1\n','posts.exe')]:
            self.assertEqual((await self.client.post('/api/analyze',content=content,headers={'X-Filename':name})).status_code,422)
        self.assertEqual((await self.client.post('/api/analyze',content=b'x'*(5*1024*1024+1))).status_code,413)
    async def test_zero_denominator_ratio_serializes_null(self):
        r=await self.client.post('/api/analyze',content=b'views,sales\n0,2\n',headers={'X-Filename':'posts.csv'})
        self.assertEqual(r.status_code,200)
        self.assertIsNone(r.json()['ratios']['sales_per_view']['percent'])
        self.assertNotIn('NaN',r.text)
        self.assertNotIn('Infinity',r.text)
    async def test_cors_allows_local_frontend(self):
        r=await self.client.options('/api/analyze',headers={'Origin':'http://localhost:8443','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type,x-filename'})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.headers['access-control-allow-origin'],'http://localhost:8443')

if __name__=='__main__': unittest.main()
