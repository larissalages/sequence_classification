import pandas as pd
import sys, os
import ujson

classes = os.listdir("data/amino")
classes = [x.replace(".txt", "") for x in classes if x.endswith(".txt") ]

folder = sys.argv[1]
output_name = sys.argv[2]
df_all = None

for filename in os.listdir(folder):
    if filename.endswith('.csv'):
        df_each = pd.read_csv(folder+filename)
        block = filename.replace(".csv","")
        for cl in classes:
            new_cls_name = "%s_class_%s" % (cl, block)
            old_conf_name = "confidence_score_%s" % (cl)
            new_conf_name = "%s_conf_score_%s" % (cl, block)
            df_each = df_each.rename(index=str, columns={cl: new_cls_name, old_conf_name: new_conf_name})
        if df_all is None:
            df_all = df_each
        else:
            df_all = df_all.merge(df_each[df_each.columns.difference(['label'])], on='id', how='inner')
print(df_all.head())
df_all.to_csv(output_name)


