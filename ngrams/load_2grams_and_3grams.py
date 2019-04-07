from google_ngram_downloader import readline_google_store
from string import punctuation
import re
import csv


def load_ngrams(my_ngram_len, indx):

    punct = punctuation+'«»—…“”*–'
    russian = "[А-Яа-я]+"
    tags = "ADJ|ADP|ADV|CONJ|NOUN|NUM|PRT|VERB"
    
    fname, url, records = next(readline_google_store(ngram_len=my_ngram_len, lang='rus', indices=[indx]))
    record = next(records)
    count = 0

    with open(str(my_ngram_len) + 'grams-' + indx + '.tsv', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        while True:
            try:
                if record.year < 1918:
                    record = next(records)
                else:
                    if len(record.ngram) > 5 \
                    and re.search(russian, record.ngram) \
                    and not re.search(tags, record.ngram):
                        writer.writerow([record.ngram,
                                        record.year,
                                        record.match_count,
                                        record.volume_count])
                        count += 1
                        record = next(records)
                    else:
                        record = next(records)
            except StopIteration:
                break

    print(str(count) + " " + indx + " " + str(my_ngram_len) + "grams saved")
    return 0


def main():

    bigram_indices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
    				'a_', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al', 'am', 'an', 'ao', 'ap', 'aq', 'ar', 'as', 'at', 'au', 'av', 'aw', 'ax', 'ay', 'az', 
    				'b_', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bk', 'bl', 'bm', 'bn', 'bo', 'bp', 'br', 'bs', 'bt', 'bu', 'bv', 'bx', 'by', 'bz', 
    				'c_', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'cg', 'ch', 'ci', 'cj', 'ck', 'cl', 'cm', 'cn', 'co', 'cp', 'cq', 'cr', 'cs', 'ct', 'cu', 'cv', 'cx', 'cy', 'cz', 
    				'd_', 'da', 'db', 'dc', 'dd', 'de', 'df', 'dg', 'dh', 'di', 'dj', 'dk', 'dl', 'dm', 'dn', 'do', 'dp', 'dr', 'ds', 'dt', 'du', 'dv', 'dw', 'dx', 'dy', 'dz', 
    				'e_', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'eg', 'eh', 'ei', 'ej', 'ek', 'el', 'em', 'en', 'eo', 'ep', 'eq', 'er', 'es', 'et', 'eu', 'ev', 'ew', 'ex', 'ey', 'ez', 
    				'f_', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff', 'fg', 'fh', 'fi', 'fj', 'fk', 'fl', 'fm', 'fn', 'fo', 'fp', 'fr', 'fs', 'ft', 'fu', 'fv', 'fx', 'fy', 'fz', 
    				'g_', 'ga', 'gb', 'gc', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gj', 'gk', 'gl', 'gm', 'gn', 'go', 'gp', 'gr', 'gs', 'gt', 'gu', 'gv', 'gx', 'gy', 'gz', 
    				'h_', 'ha', 'hb', 'hc', 'hd', 'he', 'hf', 'hg', 'hh', 'hi', 'hj', 'hk', 'hl', 'hm', 'hn', 'ho', 'hp', 'hr', 'hs', 'ht', 'hu', 'hv', 'hx', 'hy', 'hz', 
    				'i_', 'ia', 'ib', 'ic', 'id', 'ie', 'if', 'ig', 'ih', 'ii', 'ij', 'ik', 'il', 'im', 'in', 'io', 'ip', 'iq', 'ir', 'is', 'it', 'iu', 'iv', 'iw', 'ix', 'iy', 'iz', 
    				'j_', 'ja', 'jb', 'jc', 'jd', 'je', 'jf', 'jg', 'jh', 'ji', 'jj', 'jk', 'jl', 'jm', 'jn', 'jo', 'jp', 'jr', 'js', 'jt', 'ju', 'jv', 'jw', 'jx', 'jy', 'jz', 
    				'k_', 'ka', 'kb', 'kc', 'kd', 'ke', 'kf', 'kg', 'kh', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kp', 'kr', 'ks', 'kt', 'ku', 'kv', 'kx', 'ky', 'kz', 
    				'l_', 'la', 'lb', 'lc', 'ld', 'le', 'lf', 'lg', 'lh', 'li', 'lj', 'lk', 'll', 'lm', 'ln', 'lo', 'lp', 'lr', 'ls', 'lt', 'lu', 'lv', 'lw', 'lx', 'ly', 'lz', 
    				'm_', 'ma', 'mb', 'mc', 'md', 'me', 'mf', 'mg', 'mh', 'mi', 'mj', 'mk', 'ml', 'mm', 'mn', 'mo', 'mp', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz', 
    				'n_', 'na', 'nb', 'nc', 'nd', 'ne', 'nf', 'ng', 'nh', 'ni', 'nj', 'nk', 'nl', 'nm', 'nn', 'no', 'np', 'nr', 'ns', 'nt', 'nu', 'nv', 'nw', 'nx', 'ny', 'nz', 
    				'o_', 'oa', 'ob', 'oc', 'od', 'oe', 'of', 'og', 'oh', 'oi', 'oj', 'ok', 'ol', 'om', 'on', 'oo', 'op', 'or', 'os', 'ot', 'ou', 'ov', 'ow', 'ox', 'oy', 'oz', 
    				'p_', 'pa', 'pb', 'pc', 'pd', 'pe', 'pf', 'pg', 'ph', 'pi', 'pj', 'pk', 'pl', 'pm', 'pn', 'po', 'pp', 'pr', 'ps', 'pt', 'pu', 'pv', 'px', 'py', 'pz', 
    				'q_', 'qa', 'qi', 'qn', 'qu', 'qx', 
    				'r_', 'ra', 'rb', 'rc', 'rd', 're', 'rf', 'rg', 'rh', 'ri', 'rj', 'rk', 'rl', 'rm', 'rn', 'ro', 'rp', 'rr', 'rs', 'rt', 'ru', 'rv', 'rw', 'rx', 'ry', 'rz', 
    				's_', 'sa', 'sb', 'sc', 'sd', 'se', 'sf', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sp', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw', 'sx', 'sy', 'sz', 
    				't_', 'ta', 'tb', 'tc', 'td', 'te', 'tf', 'tg', 'th', 'ti', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'ts', 'tt', 'tu', 'tv', 'tw', 'tx', 'ty', 'tz', 
    				'u_', 'ua', 'ub', 'uc', 'ud', 'ue', 'uf', 'ug', 'uh', 'ui', 'uj', 'uk', 'ul', 'um', 'un', 'uo', 'up', 'ur', 'us', 'ut', 'uu', 'uv', 'ux', 'uy', 'uz', 
    				'v_', 'va', 'vb', 'vc', 'vd', 've', 'vf', 'vg', 'vh', 'vi', 'vj', 'vk', 'vl', 'vm', 'vn', 'vo', 'vp', 'vr', 'vs', 'vt', 'vu', 'vv', 'vx', 'vy', 'vz', 
    				'w_', 'wa', 'wc', 'we', 'wh', 'wi', 'wj', 'wl', 'wm', 'wn', 'wo', 'wr', 'ws', 'wt', 'wu', 'ww', 'wx', 'wy', 
    				'x_', 'xa', 'xb', 'xc', 'xd', 'xe', 'xf', 'xg', 'xh', 'xi', 'xj', 'xk', 'xl', 'xm', 'xn', 'xo', 'xp', 'xr', 'xs', 'xt', 'xu', 'xv', 'xx', 'xy', 
    				'y_', 'ya', 'yb', 'yc', 'yd', 'ye', 'yf', 'yg', 'yh', 'yi', 'yj', 'yk', 'yl', 'ym', 'yn', 'yo', 'yp', 'yr', 'ys', 'yt', 'yu', 'yv', 'yx', 'yy', 'yz', 
    				'z_', 'za', 'zb', 'zc', 'zd', 'ze', 'zf', 'zg', 'zh', 'zi', 'zj', 'zk', 'zl', 'zm', 'zn', 'zo', 'zp', 'zr', 'zs', 'zt', 'zu', 'zv', 'zw', 'zx', 'zy', 'zz',
    				'other']

    for i in bigram_indices:
        load_ngrams(2, i)
    
    trigram_indices = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
    				'a_', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'ag', 'ah', 'ai', 'aj', 'ak', 'al', 'am', 'an', 'ao', 'ap', 'aq', 'ar', 'as', 'at', 'au', 'av', 'aw', 'ax', 'ay', 'az', 
    				'b_', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bk', 'bl', 'bm', 'bn', 'bo', 'bp', 'br', 'bs', 'bt', 'bu', 'bv', 'bx', 'by', 'bz', 
    				'c_', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'cg', 'ch', 'ci', 'cj', 'ck', 'cl', 'cm', 'cn', 'co', 'cp', 'cq', 'cr', 'cs', 'ct', 'cu', 'cv', 'cx', 'cy', 'cz', 
    				'd_', 'da', 'db', 'dc', 'dd', 'de', 'df', 'dg', 'dh', 'di', 'dj', 'dk', 'dl', 'dm', 'dn', 'do', 'dp', 'dr', 'ds', 'dt', 'du', 'dv', 'dw', 'dx', 'dy', 'dz', 
    				'e_', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'eg', 'eh', 'ei', 'ej', 'ek', 'el', 'em', 'en', 'eo', 'ep', 'eq', 'er', 'es', 'et', 'eu', 'ev', 'ex', 'ey', 'ez', 
    				'f_', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff', 'fg', 'fh', 'fi', 'fj', 'fk', 'fl', 'fm', 'fn', 'fo', 'fp', 'fr', 'fs', 'ft', 'fu', 'fv', 'fx', 'fy', 'fz', 
    				'g_', 'ga', 'gb', 'gc', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gj', 'gk', 'gl', 'gm', 'gn', 'go', 'gp', 'gr', 'gs', 'gt', 'gu', 'gv', 'gx', 'gy', 'gz', 
    				'h_', 'ha', 'hb', 'hc', 'hd', 'he', 'hf', 'hg', 'hh', 'hi', 'hj', 'hk', 'hl', 'hm', 'hn', 'ho', 'hp', 'hr', 'hs', 'ht', 'hu', 'hv', 'hx', 'hy', 'hz', 
    				'i_', 'ia', 'ib', 'ic', 'id', 'ie', 'if', 'ig', 'ih', 'ii', 'ij', 'ik', 'il', 'im', 'in', 'io', 'ip', 'iq', 'ir', 'is', 'it', 'iu', 'iv', 'iw', 'ix', 'iy', 'iz', 
    				'j_', 'ja', 'jb', 'jc', 'jd', 'je', 'jf', 'jg', 'jh', 'ji', 'jj', 'jk', 'jl', 'jm', 'jn', 'jo', 'jp', 'jr', 'js', 'jt', 'ju', 'jv', 'jw', 'jx', 'jy', 'jz', 
    				'k_', 'ka', 'kb', 'kc', 'kd', 'ke', 'kf', 'kg', 'kh', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kp', 'kr', 'ks', 'kt', 'ku', 'kv', 'kx', 'ky', 'kz', 
    				'l_', 'la', 'lb', 'lc', 'ld', 'le', 'lf', 'lg', 'lh', 'li', 'lj', 'lk', 'll', 'lm', 'ln', 'lo', 'lp', 'lr', 'ls', 'lt', 'lu', 'lv', 'lx', 'ly', 'lz', 
    				'm_', 'ma', 'mb', 'mc', 'md', 'me', 'mf', 'mg', 'mh', 'mi', 'mj', 'mk', 'ml', 'mm', 'mn', 'mo', 'mp', 'mr', 'ms', 'mt', 'mu', 'mv', 'mx', 'my', 'mz', 
    				'n_', 'na', 'nb', 'nc', 'nd', 'ne', 'nf', 'ng', 'nh', 'ni', 'nj', 'nk', 'nl', 'nm', 'nn', 'no', 'np', 'nr', 'ns', 'nt', 'nu', 'nv', 'nw', 'nx', 'ny', 'nz', 
    				'o_', 'oa', 'ob', 'oc', 'od', 'oe', 'of', 'og', 'oh', 'oi', 'oj', 'ok', 'ol', 'om', 'on', 'oo', 'op', 'or', 'os', 'ot', 'ou', 'ov', 'ow', 'ox', 'oy', 'oz', 
    				'p_', 'pa', 'pb', 'pc', 'pd', 'pe', 'pf', 'pg', 'ph', 'pi', 'pj', 'pk', 'pl', 'pm', 'pn', 'po', 'pp', 'pr', 'ps', 'pt', 'pu', 'pv', 'px', 'py', 'pz', 
    				'q_', 'qa', 'qn', 'qu', 'qx', 
    				'r_', 'ra', 'rb', 'rc', 'rd', 're', 'rf', 'rg', 'rh', 'ri', 'rj', 'rk', 'rl', 'rm', 'rn', 'ro', 'rp', 'rr', 'rs', 'rt', 'ru', 'rv', 'rw', 'rx', 'ry', 'rz', 
    				's_', 'sa', 'sb', 'sc', 'sd', 'se', 'sf', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sp', 'sq', 'sr', 'ss', 'st', 'su', 'sv', 'sw', 'sx', 'sy', 'sz', 
    				't_', 'ta', 'tb', 'tc', 'td', 'te', 'tf', 'tg', 'th', 'ti', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'ts', 'tt', 'tu', 'tv', 'tw', 'tx', 'ty', 'tz', 
    				'u_', 'ua', 'ub', 'uc', 'ud', 'ue', 'uf', 'ug', 'uh', 'ui', 'uj', 'uk', 'ul', 'um', 'un', 'uo', 'up', 'ur', 'us', 'ut', 'uu', 'uv', 'ux', 'uy', 'uz', 
    				'v_', 'va', 'vb', 'vc', 'vd', 've', 'vf', 'vg', 'vh', 'vi', 'vj', 'vk', 'vl', 'vm', 'vn', 'vo', 'vp', 'vr', 'vs', 'vt', 'vu', 'vv', 'vx', 'vy', 'vz', 
    				'w_', 'wa', 'we', 'wh', 'wi', 'wj', 'wl', 'wn', 'wo', 'wr', 'ws', 'wt', 'wu', 'ww', 'wx', 
    				'x_', 'xa', 'xc', 'xd', 'xe', 'xf', 'xg', 'xh', 'xi', 'xj', 'xk', 'xl', 'xm', 'xn', 'xo', 'xp', 'xr', 'xs', 'xt', 'xu', 'xv', 'xx', 'xy', 
    				'y_', 'ya', 'yb', 'yc', 'yd', 'ye', 'yf', 'yg', 'yh', 'yi', 'yj', 'yk', 'yl', 'ym', 'yn', 'yo', 'yp', 'yr', 'ys', 'yt', 'yu', 'yv', 'yx', 'yy', 'yz', 
    				'z_', 'za', 'zb', 'zc', 'zd', 'ze', 'zf', 'zg', 'zh', 'zi', 'zj', 'zk', 'zl', 'zm', 'zn', 'zo', 'zp', 'zr', 'zs', 'zt', 'zu', 'zv', 'zw', 'zx', 'zy', 'zz', 
    				'other']

    for i in trigram_indices:
        load_ngrams(3, i)

    return 0
        

if __name__ == '__main__':
    main()