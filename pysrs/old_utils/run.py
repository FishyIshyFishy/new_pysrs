'''old functions, helpful to have for reference though'''
# def raster_scan(ai_channels, galvo):
#     if isinstance(ai_channels, str):
#         ai_channels = [ai_channels]

#     with nidaqmx.Task() as ao_task, nidaqmx.Task() as ai_task:
#         ao_channels = list(galvo.ao_chans)
#         composite_wave = galvo.waveform.copy()

#         for chan in ao_channels:
#             ao_task.ao_channels.add_ao_voltage_chan(f'{galvo.device}/{chan}')
#         ao_task.timing.cfg_samp_clk_timing(
#             rate=galvo.rate,
#             sample_mode=AcquisitionType.FINITE,
#             samps_per_chan=composite_wave.shape[1]
#         )

#         for ch in ai_channels:
#             ai_task.ai_channels.add_ai_voltage_chan(ch)

#         ao_task.timing.cfg_samp_clk_timing(
#             rate=galvo.rate,
#             sample_mode=AcquisitionType.FINITE,
#             samps_per_chan=galvo.total_samples
#         )
#         ai_task.timing.cfg_samp_clk_timing(
#             rate=galvo.rate,
#             source=f'/{galvo.device}/ao/SampleClock',
#             sample_mode=AcquisitionType.FINITE,
#             samps_per_chan=galvo.total_samples
#         )

#         ao_task.write(composite_wave, auto_start=False)
#         ai_task.start()
#         ao_task.start()

#         ao_task.wait_until_done(timeout=galvo.total_samples / galvo.rate + 5)
#         ai_task.wait_until_done(timeout=galvo.total_samples / galvo.rate + 5)

#         acq_data = np.array(ai_task.read(number_of_samples_per_channel=galvo.total_samples))

#     n_ch = len(ai_channels)
#     results = []

#     if n_ch == 1:
#         # shape is (total_y, total_x, pixel_samples), dont forget that u dummy
#         acq_data = acq_data.reshape(galvo.total_y, galvo.total_x, galvo.pixel_samples)
#         data2d = np.mean(acq_data, axis=2)

#         # crop out extrasteps_left and extrasteps_right
#         x1 = galvo.extrasteps_left
#         x2 = galvo.extrasteps_left + galvo.numsteps_x
#         cropped = data2d[:, x1:x2]
#         return [cropped]
#     else:
#         for i in range(n_ch):
#             chan_data = acq_data[i].reshape(galvo.total_y, galvo.total_x, galvo.pixel_samples)
#             data2d = np.mean(chan_data, axis=2)

#             x1 = galvo.extrasteps_left
#             x2 = galvo.extrasteps_left + galvo.numsteps_x
#             cropped = data2d[:, x1:x2]
#             results.append(cropped)
#         return results

# def raster_scan_rpoc(ai_channels, galvo, mask, do_chan="port0/line5", modulate=False, mod_do_chans=None, mod_masks=None):
#     if isinstance(ai_channels, str):
#         ai_channels = [ai_channels]

#     with nidaqmx.Task() as ao_task, nidaqmx.Task() as ai_task, nidaqmx.Task() as do_task:
#         ao_channels = list(galvo.ao_chans)
#         composite_wave = galvo.waveform.copy()  
#         for chan in ao_channels:
#             ao_task.ao_channels.add_ao_voltage_chan(f'{galvo.device}/{chan}')
#         ao_task.timing.cfg_samp_clk_timing(
#             rate=galvo.rate,
#             sample_mode=AcquisitionType.FINITE,
#             samps_per_chan=composite_wave.shape[1]
#         )

#         for ch in ai_channels:
#             ai_task.ai_channels.add_ai_voltage_chan(ch)
#         ai_task.timing.cfg_samp_clk_timing(
#             rate=galvo.rate,
#             source=f'/{galvo.device}/ao/SampleClock',
#             sample_mode=AcquisitionType.FINITE,
#             samps_per_chan=galvo.total_samples
#         )

#         if modulate and mod_do_chans and mod_masks:
#             if len(mod_do_chans) != len(mod_masks):
#                 raise ValueError("The number of modulation DO channels and masks must match.")
#             ttl_signals = []
#             for m in mod_masks:
#                 if isinstance(m, Image.Image):
#                     m_arr = np.array(m)
#                 else:
#                     m_arr = m
#                 if m_arr.shape[0] != galvo.numsteps_y or m_arr.shape[1] != galvo.numsteps_x:
#                     m_arr = np.array(Image.fromarray(m_arr.astype(np.uint8)*255).resize((galvo.numsteps_x, galvo.numsteps_y), Image.NEAREST)) > 128
#                 padded_mask = []
#                 for row_idx in range(galvo.numsteps_y):
#                     row_data = m_arr[row_idx, :]
#                     padded_row = np.concatenate((
#                         np.zeros(galvo.extrasteps_left, dtype=bool),
#                         row_data,
#                         np.zeros(galvo.extrasteps_right, dtype=bool)
#                     ))
#                     padded_mask.append(padded_row)
#                 padded_mask = np.array(padded_mask, dtype=bool)
#                 flattened = padded_mask.ravel()
#                 ttl_signal = np.repeat(flattened, galvo.pixel_samples).astype(bool)
#                 ttl_signals.append(ttl_signal)
#             for chan in mod_do_chans:
#                 do_task.do_channels.add_do_chan(f"{galvo.device}/{chan}")
#             do_task.timing.cfg_samp_clk_timing(
#                 rate=galvo.rate,
#                 source=f'/{galvo.device}/ao/SampleClock',
#                 sample_mode=AcquisitionType.FINITE,
#                 samps_per_chan=galvo.total_samples
#             )
#             do_task.write(ttl_signals, auto_start=False)
#         else:
#             if isinstance(mask, Image.Image):
#                 mask = np.array(mask)
#             if not isinstance(mask, np.ndarray):
#                 raise TypeError('Mask must be a numpy array or PIL Image.')
#             padded_mask = []
#             for row_idx in range(galvo.numsteps_y):
#                 row_data = mask[row_idx, :]
#                 padded_row = np.concatenate((
#                     np.zeros(galvo.extrasteps_left, dtype=bool),
#                     row_data,
#                     np.zeros(galvo.extrasteps_right, dtype=bool)
#                 ))
#                 padded_mask.append(padded_row)
#             padded_mask = np.array(padded_mask, dtype=bool)
#             flattened = padded_mask.ravel()
#             ttl_signal = np.repeat(flattened, galvo.pixel_samples).astype(bool)
#             do_task.do_channels.add_do_chan(f"{galvo.device}/{do_chan}")
#             do_task.timing.cfg_samp_clk_timing(
#                 rate=galvo.rate,
#                 source=f'/{galvo.device}/ao/SampleClock',
#                 sample_mode=AcquisitionType.FINITE,
#                 samps_per_chan=galvo.total_samples
#             )
#             do_task.write(ttl_signal.tolist(), auto_start=False)

#         ao_task.write(composite_wave, auto_start=False)
#         ai_task.start()
#         do_task.start()
#         ao_task.start()

#         ao_task.wait_until_done(timeout=galvo.total_samples / galvo.rate + 5)
#         do_task.wait_until_done(timeout=galvo.total_samples / galvo.rate + 5)
#         ai_task.wait_until_done(timeout=galvo.total_samples / galvo.rate + 5)

#         acq_data = np.array(ai_task.read(number_of_samples_per_channel=galvo.total_samples))

#     n_ch = len(ai_channels)
#     results = []
#     if n_ch == 1:
#         acq_data = acq_data.reshape(galvo.total_y, galvo.total_x, galvo.pixel_samples)
#         data2d = np.mean(acq_data, axis=2)
#         x1 = galvo.extrasteps_left
#         x2 = galvo.extrasteps_left + galvo.numsteps_x
#         cropped = data2d[:, x1:x2]
#         results = [cropped]
#     else:
#         for i in range(n_ch):
#             chan_data = acq_data[i].reshape(galvo.total_y, galvo.total_x, galvo.pixel_samples)
#             data2d = np.mean(chan_data, axis=2)
#             x1 = galvo.extrasteps_left
#             x2 = galvo.extrasteps_left + galvo.numsteps_x
#             cropped = data2d[:, x1:x2]
#             results.append(cropped)
#     return results


# def variable_scan_rpoc(ai_channels, galvo, mask, dwell_multiplier=2.0, modulate=False, mod_masks=None):
#     if isinstance(ai_channels, str):
#         ai_channels = [ai_channels]

#     if modulate and mod_masks:
#         gen_mask = mod_masks[0]
#     else:
#         gen_mask = mask

#     if isinstance(gen_mask, Image.Image):
#         gen_mask = np.array(gen_mask)
#     if not isinstance(gen_mask, np.ndarray):
#         raise TypeError("Mask must be a NumPy array or PIL Image.")
#     gen_mask = gen_mask > 128

#     x_wave, y_wave, pixel_map = galvo.gen_variable_waveform(gen_mask, dwell_multiplier)
    
#     if modulate and mod_masks:
#         ttl_signals = []
#         for m in mod_masks:
#             if isinstance(m, Image.Image):
#                 m_arr = np.array(m)
#             else:
#                 m_arr = m
#             m_arr = m_arr > 128  
#             padded_mask = []
#             for row_idx in range(galvo.numsteps_y):
#                 row_data = m_arr[row_idx, :]
#                 padded_row = np.concatenate((
#                     np.zeros(galvo.extrasteps_left, dtype=bool),
#                     row_data,
#                     np.zeros(galvo.extrasteps_right, dtype=bool)
#                 ))
#                 padded_mask.append(padded_row)
#             padded_mask = np.array(padded_mask, dtype=bool)
#             flattened = padded_mask.ravel()
#             ttl_signal = np.repeat(flattened, galvo.pixel_samples).astype(bool)
#             ttl_signals.append(ttl_signal)
#     else:
#         if isinstance(mask, Image.Image):
#             mask = np.array(mask)
#         mask = mask > 128
#         padded_mask = []
#         for row_idx in range(galvo.numsteps_y):
#             row_data = mask[row_idx, :]
#             padded_row = np.concatenate((
#                 np.zeros(galvo.extrasteps_left, dtype=bool),
#                 row_data,
#                 np.zeros(galvo.extrasteps_right, dtype=bool)
#             ))
#             padded_mask.append(padded_row)
#         padded_mask = np.array(padded_mask, dtype=bool)
#         flattened = padded_mask.ravel()
#         ttl_signal = np.repeat(flattened, galvo.pixel_samples).astype(bool)
    
#     with nidaqmx.Task() as ao_task, nidaqmx.Task() as ai_task, nidaqmx.Task() as do_task:
#         for chan in galvo.ao_chans:
#             ao_task.ao_channels.add_ao_voltage_chan(f"{galvo.device}/{chan}")
#         for ch in ai_channels:
#             ai_task.ai_channels.add_ai_voltage_chan(ch)

#         total_samps = len(x_wave)
#         ao_task.timing.cfg_samp_clk_timing(
#             rate=galvo.rate,
#             sample_mode=AcquisitionType.FINITE,
#             samps_per_chan=total_samps
#         )
#         ai_task.timing.cfg_samp_clk_timing(
#             rate=galvo.rate,
#             source=f"/{galvo.device}/ao/SampleClock",
#             sample_mode=AcquisitionType.FINITE,
#             samps_per_chan=total_samps
#         )

#         if modulate and mod_masks:
#             num_mod = len(ttl_signals)
#             for i in range(num_mod):
#                 do_task.do_channels.add_do_chan(f"{galvo.device}/port0/line{5+i}")
#             do_task.timing.cfg_samp_clk_timing(
#                 rate=galvo.rate,
#                 source=f"/{galvo.device}/ao/SampleClock",
#                 sample_mode=AcquisitionType.FINITE,
#                 samps_per_chan=total_samps
#             )
#             do_task.write(ttl_signals, auto_start=False)
#         else:
#             do_task.do_channels.add_do_chan(f"{galvo.device}/port0/line5")
#             do_task.timing.cfg_samp_clk_timing(
#                 rate=galvo.rate,
#                 source=f"/{galvo.device}/ao/SampleClock",
#                 sample_mode=AcquisitionType.FINITE,
#                 samps_per_chan=total_samps
#             )
#             do_task.write(ttl_signal.tolist(), auto_start=False)

#         composite_wave = np.vstack([x_wave, y_wave])
#         ao_task.write(composite_wave, auto_start=False)

#         ai_task.start()
#         do_task.start()
#         ao_task.start()
#         ao_task.wait_until_done(timeout=total_samps / galvo.rate + 5)
#         ai_task.wait_until_done(timeout=total_samps / galvo.rate + 5)

#         acq_data = np.array(ai_task.read(number_of_samples_per_channel=total_samps))

#     n_channels = len(ai_channels)
#     results = []
#     if n_channels == 1:
#         pixel_values_2d = partition_and_average(acq_data, gen_mask, pixel_map, galvo)
#         x1 = galvo.extrasteps_left
#         x2 = x1 + galvo.numsteps_x
#         cropped = pixel_values_2d[:, x1:x2]
#         results = [cropped]
#     else:
#         for ch_idx in range(n_channels):
#             ch_data = acq_data[ch_idx]
#             pixel_values_2d = partition_and_average(ch_data, gen_mask, pixel_map, galvo)
#             x1 = galvo.extrasteps_left
#             x2 = x1 + galvo.numsteps_x
#             cropped = pixel_values_2d[:, x1:x2]
#             results.append(cropped)
#     return results