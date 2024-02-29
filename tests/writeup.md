### Evaluation

Text, while prevalent across the Web, poses challenges in information extraction from web pages. The question arises: should the approach to tool development be tailored to specific news outlets or blogs (leading to the creation of web scraping tools), or should it aim for a broad applicability to enable the opportunistic collection of information?

The focus of extraction is on isolating the primary content, typically found in the center of the page, excluding sidebars, headers, and footers, yet potentially incorporating titles and, where applicable, comments. This process is referred to by various terms such as web scraping, boilerplate removal, DOM-based content extraction, main content identification, or web page cleaning.

### Description

#### Test Set
The experiments are conducted on a diverse set of documents typical of Internet articles, such as news outlets and blogs. Challenges arise from documents featuring mixed content like lists and tables, or those with partially invalid HTML. The selection encompasses web pages primarily in German, with a significant portion (20-30%) in other languages including English, French, various European languages, Chinese, and Arabic, to ensure a comprehensive analysis.

#### Evaluation
Key segments of documents are identified that, while not statistically representative, hold substantial significance for text analysis. This includes peripheral elements like left/right columns, additional headers, author details, footers with imprints or addresses, and links to affiliated and social networks, collectively referred to as boilerplate. The focus is also on extracting raw text segments, serving as a measure of HTML extraction quality.

#### Time
Execution time is noted as a reference. With the baseline extraction being straightforward and quick, it serves as the benchmark. Certain tools, specifically goose3 and newspaper, lag behind others in speed, and news-please stands out due to its comprehensive operations beyond mere text extraction. Nerobot's and readabilipy's slow performance is noted without clear cause.

#### Errors
Tools such as Nerobot, boilerpy3, newspaper3k, and readabilipy encounter errors across various HTML files in the test set, likely due to malformed HTML, encoding, or parsing issues. These errors are overlooked for the sake of completing the benchmark.

#### Results

#### Results for all 750 urls (January 2024)
| Tool                 | True Positives | False Positives | True Negatives | False Negatives | Time (s)   | Precision | Recall | Accuracy | F-Score | Time Diff. (s) |
|----------------------|----------------|-----------------|----------------|-----------------|------------|-----------|--------|----------|---------|----------------|
| Baseline             | 1886           | 610             | 1640           | 350             | 3.96       | 0.756     | 0.843  | 0.786    | 0.797   | -              |
| Nero                 | 1605           | 548             | 1702           | 631             | 5174.64    | 0.745     | 0.718  | 0.737    | 0.731   | 1307.13        |
| Html2Text            | 1586           | 1677            | 573            | 650             | 52.74      | 0.486     | 0.709  | 0.481    | 0.577   | 13.32          |
| Html_Text            | 2142           | 1906            | 344            | 94              | 7.65       | 0.529     | 0.958  | 0.554    | 0.682   | 1.93           |
| Inscriptis           | 2146           | 1880            | 370            | 90              | 14.68      | 0.533     | 0.960  | 0.561    | 0.685   | 3.71           |
| JusText              | 1453           | 227             | 2023           | 783             | 23.46      | 0.865     | 0.650  | 0.775    | 0.742   | 5.93           |
| Goose                | 1527           | 108             | 2142           | 709             | 96.48      | 0.934     | 0.683  | 0.818    | 0.789   | 24.37          |
| Newspaper            | 1325           | 156             | 2094           | 911             | 50.93      | 0.895     | 0.593  | 0.762    | 0.713   | 12.86          |
| Boilerpipe           | 1663           | 381             | 1869           | 573             | 16.52      | 0.814     | 0.744  | 0.787    | 0.777   | 4.17           |
| NewsPlease           | 1643           | 186             | 2064           | 593             | 653.37     | 0.898     | 0.735  | 0.826    | 0.808   | 165.04         |
| Readability          | 1629           | 200             | 2050           | 607             | 25.74      | 0.891     | 0.729  | 0.820    | 0.801   | 6.50           |
| ReadabiliPy          | 1951           | 278             | 1972           | 285             | 643.60     | 0.875     | 0.873  | 0.874    | 0.874   | 162.58         |
| BS4                  | 2045           | 1784            | 466            | 191             | 24.45      | 0.534     | 0.915  | 0.560    | 0.674   | 6.18           |
| Trafilatura          | 1992           | 191             | 2059           | 244             | 18.55      | 0.913     | 0.891  | 0.903    | 0.902   | 4.69           |
| Trafilatura + X      | 2027           | 191             | 2059           | 209             | 27.17      | 0.914     | 0.907  | 0.911    | 0.910   | 6.86           |
| Trafilatura Precision| 1968           | 159             | 2091           | 268             | 37.69      | 0.925     | 0.880  | 0.905    | 0.902   | 9.52           |
| Trafilatura Recall   | 2037           | 231             | 2019           | 199             | 20.24      | 0.898     | 0.911  | 0.904    | 0.905   | 5.11           |

#### Results with 676 urls (January 2024)
| Tool                 | True Positives | False Positives | True Negatives | False Negatives | Time (s)    | Precision | Recall | Accuracy | F-Score | Time Diff. (s) |
|----------------------|----------------|-----------------|----------------|-----------------|-------------|-----------|--------|----------|---------|----------------|
| Baseline             | 1689           | 570             | 1476           | 335             | 2.916       | 0.748     | 0.834  | 0.778    | 0.789   | -              |
| Nero                 | 1678           | 561             | 1485           | 346             | 4711.300    | 0.749     | 0.829  | 0.777    | 0.787   | 1615.47        |
| Html2Text            | 1425           | 1516            | 530            | 599             | 40.623      | 0.485     | 0.704  | 0.480    | 0.574   | 13.93          |
| Html_Text            | 1938           | 1720            | 326            | 86              | 5.869       | 0.530     | 0.958  | 0.556    | 0.682   | 2.01           |
| Inscriptis           | 1941           | 1697            | 349            | 83              | 11.367      | 0.534     | 0.959  | 0.563    | 0.686   | 3.90           |
| Justext              | 1318           | 208             | 1838           | 706             | 17.431      | 0.864     | 0.651  | 0.775    | 0.743   | 5.98           |
| Goose                | 1386           | 99              | 1947           | 638             | 74.724      | 0.933     | 0.685  | 0.819    | 0.790   | 25.62          |
| Newspaper            | 1193           | 148             | 1898           | 831             | 37.551      | 0.890     | 0.589  | 0.759    | 0.709   | 12.88          |
| Boilerpipe           | 1512           | 360             | 1686           | 512             | 13.786      | 0.808     | 0.747  | 0.786    | 0.776   | 4.73           |
| Newsplease           | 1484           | 176             | 1870           | 540             | 267.158     | 0.894     | 0.733  | 0.824    | 0.806   | 91.61          |
| Readability          | 1452           | 190             | 1856           | 572             | 18.789      | 0.884     | 0.717  | 0.813    | 0.792   | 6.44           |
| Readabilipy          | 1761           | 264             | 1782           | 263             | 524.169     | 0.870     | 0.870  | 0.871    | 0.870   | 179.73         |
| BS4                  | 1846           | 1610            | 436            | 178             | 20.485      | 0.534     | 0.912  | 0.561    | 0.674   | 7.02           |
| Trafilatura          | 1788           | 182             | 1864           | 236             | 13.599      | 0.908     | 0.883  | 0.897    | 0.895   | 4.66           |
| Trafilatura + X      | 1826           | 185             | 1861           | 198             | 21.012      | 0.908     | 0.902  | 0.906    | 0.905   | 7.20           |
| Trafilatura Precision| 1773           | 151             | 1895           | 251             | 28.422      | 0.922     | 0.876  | 0.901    | 0.898   | 9.75           |
| Trafilatura Recall   | 1834           | 222             | 1824           | 190             | 15.173250198364258      | 0.892  | 0.906    | 0.899   | 0.899   | 5.20           |

