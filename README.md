# Readme - Dat
# 🐍 Hướng dẫn cài đặt Conda và tạo môi trường ảo

## 1. Tải và cài đặt Miniconda

Miniconda là phiên bản nhẹ hơn của Anaconda, chỉ bao gồm `conda` và một số công cụ cơ bản. Phù hợp cho người dùng muốn kiểm soát môi trường tốt hơn.

### 🔗 Link tải Miniconda: [Link cài đặt official](https://www.anaconda.com/docs/getting-started/miniconda/install#)
- [Miniconda cho Windows](https://youtu.be/AgnAs0nPEVg)

### ⚙️ Các bước cài đặt (Windows):
1. Tải file `.exe` phù hợp với hệ điều hành.
2. Chạy file cài đặt và chọn:
   - ✅ Add Miniconda to `PATH` (khuyến nghị bật)
   - ✅ Register Miniconda as the system's default Python
3. Mở Terminal (`cmd`, `PowerShell` hoặc `Anaconda Prompt`).

---

## 2. Kiểm tra cài đặt Conda

```bash
conda --version
```

## 3. Tạo môi trường mới
`ten_moi_truong` thì do bản thân tự đặt (như đặt tên biến trong code Python)
```bash
conda create --name ten_moi_truong python=3.10
```

## 4. Kích hoạt môi trường
```bash
conda activate ten_moi_truong
```
## 5. Cài đặt thêm gói vào môi trường
```bash
conda install ten_goi
```
Ví dụ:

```bash
conda install matplotlib seaborn
```
Hoặc cài từ pip:

```bash
pip install scikit-learn
```


## Chạy code của bản này

### Command-Line Arguments

The model can be configured using the following command-line arguments:

- `--model`: The type of model to use (default: `gcn_vae`)
- `--seed`: Random seed for reproducibility (default: 42)
- `--epochs`: Number of epochs to train (default: 10000)
- `--hidden1`: Number of units in the first hidden layer (default: 8)
- `--hidden2`: Number of units in the second hidden layer (default: 2)
- `--lr`: Initial learning rate (default: 0.05)
- `--dropout`: Dropout rate (default: 0.0)
- `--dataset`: Type of dataset to use (default: `cora`)
- `--cluster`: Number of communities to detect (default: 7)

### Running the Model

Để chạy code: 
1. Donwload anaconda như trên
2. Khởi tạo môi trường conda mới, đặt terminal tại vị trí thư mục `VGAER`
2. Cài đặt những gì yêu cầu từ gói: 
```bash
pip install -r requirements.txt
```
3. Để chạy thử
```bash

cd VGAER_codes 
python main.py --model gcn_vae --dataset cora --cluster 7
```

This will train the VGAER model on the Cora dataset with 7 communities.
4. Để custom đối với đồ thị mới: 
   * Sử dụng đồ thị khác trong package `dgl.data`, ví dụ như trong code thuần, họ sử dụng được 3 bộ như sau: `from dgl.data import CoraGraphDataset, CiteseerGraphDataset , PubmedGraphDataset`, vậy nên ta có thể sử dụng các bộ khác từ `dgl.data` đó
   * Custom thêm đồ thị trong hàm `vgaer` trong file `train_vgaer.py` - như là các custom dataset họ để trong thư mục `dataset`:
   ```python
   G = nx.read_gml('dataset/netscience/netscience.gml', label='id')
    A = torch.Tensor(nx.adjacency_matrix(G).todense())
    A_orig = A.detach().numpy()
    A_orig_ten = A
    A_orig_ten = A_orig_ten.to(device)

    columns = ['Source', 'Target']
    data = pd.read_csv('data/lastfm_asia/lastfm_asia_edges.csv', names=columns, header=None)
    G = nx.Graph()
    data_len = len(data)
    for i in range(data_len):
        G.add_edge(data.iloc[i]['Source'], data.iloc[i]['Target'])

    A = torch.Tensor(nx.adjacency_matrix(G).todense())
    A_orig = A.detach().numpy()
    A_orig_ten = A.to(device)
   ```

## Code Structure

- `model.py`: Contains the implementation of the VGAER model.
- `cluster.py`: Contains community detection algorithms.
- `NMI.py`: Contains the Normalized Mutual Information (NMI) score calculation.
- `Qvalue.py`: Contains the Q value calculation for community detection.
- `main.py`: The main script that loads the dataset, trains the model, and performs community detection.


# Requirement

dgl
matplotlib==3.5.1

networkx==2.7.1

numpy==1.22.3

pandas==1.4.1

scikit_learn==1.0.2

scipy==1.8.0

seaborn==0.11.2

torch==1.11.0

# Citation

Please cite our paper if you use this code or our model in your own work:

@inproceedings{qiu2022VGAER,\
              title={VGAER: Graph Neural Network Reconstruction based Community
Detection},\
              author={Qiu, Chenyang and Huang, Zhaoci and Xu, Wenzhe and Li, Huijia},       
              booktitle={AAAI: DLG-AAAI'22},              
              year={2022}              
 }
