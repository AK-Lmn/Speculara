from pathlib import Path
import pandas as pd
import numpy as np

root = Path(__file__).resolve().parents[1] / 'public' / 'demo'
root.mkdir(parents=True,exist_ok=True)
rng = np.random.default_rng(2026)
records=[]
for i,date in enumerate(pd.date_range('2026-09-01',periods=42)):
    category=['Tutorial reel','Product carousel','Founder story'][i%3]
    views=int(1400+i*24+rng.integers(-250,251))
    saves=int(views*(.06 if i%3==0 else .025)+rng.integers(0,12))
    sales=int(views*(.012 if i%3==1 else .006)+rng.integers(0,4))
    records.append(dict(date=date.strftime('%Y-%m-%d'),post_id=f'SYNTH-{i+1:03}',category=category,region=['Metro Manila','Cebu','Davao'][i%3],views=views,likes=int(views*.08),saves=saves,comments=int(rng.integers(12,65)),sales=sales,dataset_label='SYNTHETIC FICTIONAL DEMO'))
df=pd.DataFrame(records)
df.to_csv(root/'speculara-synthetic.csv',index=False)
df.to_excel(root/'speculara-synthetic.xlsx',index=False)
# Separate comment-level data avoids repeated whole-post totals.
pd.DataFrame({'post_id':['SYNTH-001','SYNTH-001','SYNTH-002','SYNTH-003','SYNTH-003','SYNTH-004'], 'text':['Love this tutorial, salamat!','Where can I buy this?','Please restock the blue bag','Shipping was bad, box broken','Not good for my needs','Maganda! How much?'], 'dataset_label':['SYNTHETIC FICTIONAL COMMENTS']*6}).to_csv(root/'speculara-text-synthetic.csv',index=False)
print('Generated fictional demo files:',len(df),'post records; 6 separate text records')
