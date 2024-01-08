def batch_iterator(data, batch_size):
    while data:
        batch = data[:batch_size]
        data = data[batch_size:]
        yield batch
