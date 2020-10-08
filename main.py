import tensorflow as tf
import pandas as pd
import pymysql
import time
import os
import genius
import mydb
import myutils
import generator


def scrape(artist):
    count = 0
    scrape_df = pd.DataFrame(columns=['Artist', 'Url', 'Title', 'Lyrics'])

    print('Now Scraping : ' + artist)
    gs = genius.GeniusScraper(artist)
    urls = gs.get_urls()
    print('url scraping finished...')

    for url in urls:
        title, lyrics = genius.get_title_lyrics(url)

        time.sleep(3)
        df_dict = {'Artist': artist, 'Url': url, 'Title': title, 'Lyrics': lyrics}
        scrape_df = scrape_df.append(df_dict, ignore_index=True)

        myutils.progress_bar(count, len(urls))
        count += 1

    return scrape_df


def scrape_to_db(sdb, artist, df):
    sdb.create_table()

    for i in range(len(df)):
        try:
            sdb.insert_data(df['Artist'][i], df['Url'][i], df['Title'][i], df['Lyrics'][i])
        except pymysql.Error:
            continue

    table = sdb.get_data(artist)
    tb_df = pd.DataFrame(table)
    print(tb_df.head())


def get_dataset(gen, seq_length, buffer_size, batch_size):
    lyrics_dataset = tf.data.Dataset.from_tensor_slices(gen.idx_lyrics)

    sequences = lyrics_dataset.batch(seq_length + 1, drop_remainder=True)
    dataset = sequences.map(gen.xy_split)

    dataset = dataset.shuffle(buffer_size).batch(batch_size, drop_remainder=True)

    return dataset


def main():
    # ---Scraping---
    sdb = mydb.ScrapeDB(user='root', password='****************', db='testdb')

    artist = input('Artist : ')
    sdf = scrape(artist)
    scrape_to_db(sdb, artist, sdf)

    table = sdb.get_all_data()
    lyrics = [str(row['Lyrics']) for row in table]

    sdb.con.close()

    # ---Lyrics Generation---
    # variables
    seq_length = 100
    batch_size = 64
    buffer_size = 10000

    embedding_dim = 256
    rnn_units = 1024
    epochs = 10

    # checkpoint setting
    cp_dir = './training_checkpoints'
    cp_path = os.path.join(cp_dir, "ckpt_{epoch}")
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=cp_path, save_weights_only=True)

    # model
    lg = generator.LyricsGenerator(lyrics)
    dataset = get_dataset(lg, seq_length, buffer_size, batch_size)

    model = lg.model(
        embedding_dim=embedding_dim,
        rnn_units=rnn_units,
        batch_size=batch_size
    )

    model.compile(optimizer='adam', loss=lg.loss)
    model.fit(dataset, epochs=epochs, callbacks=[cp_callback])

    pred_model = lg.model(embedding_dim, rnn_units, batch_size=1)
    pred_model.load_weights(tf.train.latest_checkpoint(cp_dir))
    pred_model.build(tf.TensorShape([1, None]))

    print(lg.generate_lyrics(pred_model, 'i love you'))


if __name__ == '__main__':
    main()
